from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q, Prefetch
from tracker.models import Project, Priority, Status, Task, Comment
from tracker.paginations import CustomPagination
from tracker.serializer import ProjectSerializer, PrioritySerializer, StatusSerializer, TaskSerializer, \
    CommentSerializer
from tracker.services import get_full_name
from users.models import User
from users.permissions import IsOwner, IsStaff


@api_view(['GET'])
def busy_employees(request):
    """Запрашивает из БД список сотрудников и их задачи, отсортированный по количеству активных задач."""
    # Задачи со статусом "в работе"
    tasks_in_progress = Task.objects.filter(status__slug='v-rabote')

    # Сотрудники с добавленным полем количества задач со статусом "в работе" и заранее сформированным списком названий задач
    employees = User.objects.annotate(
        active_tasks_count=Count('tasks', filter=Q(tasks__status__slug='v-rabote'))
    ).prefetch_related(
        Prefetch('tasks', queryset=tasks_in_progress, to_attr='active_tasks_list')
    ).order_by('-active_tasks_count')

    data = []
    # Цикл по формированию выводных данных
    for emp in employees:
        active_tasks_titles = [task.title for task in getattr(emp, 'active_tasks_list', [])]
        data.append({
            'executor': get_full_name(emp),
            'active_tasks_count': len(active_tasks_titles),
            'active_tasks_titles': active_tasks_titles,
        })
    return Response(data)


@api_view(['GET'])
def important_tasks(request):
    """Задачи, не взяты в работу, но от которых зависят другие задачи, взятые в работу"""
    # Задачи, со статусом "новая", у которых есть родительская задача со статусом "в работе"
    not_started_tasks = Task.objects.filter(
        status__slug='novaja',
        parent_task__status__slug='v-rabote').distinct().prefetch_related(
        'parent_task__executor')

    # Наименее загруженный сотрудник
    least_loaded_employee = User.objects.annotate(
        active_tasks_count=Count('tasks', filter=Q(tasks__status__slug='v-rabote'))
    ).order_by('active_tasks_count').first()

    results = []


 # Цикл перебора задач со статусом "новая"
    for task in not_started_tasks:
        candidates = []

        # Исполнитель родительской задачи
        parent_executor = None
        if task.parent_task and task.parent_task.executor:
            parent_executor = task.parent_task.executor
            parent_load = parent_executor.tasks.filter(status__slug='v-rabote').count()
            least_load = least_loaded_employee.active_tasks_count if least_loaded_employee else 0

            # Проверка условия по загрузке исполнителя родительской задачи
            if parent_load <= least_load + 2:
                candidates.append(f"{get_full_name(parent_executor)}")

        # Если нет подходящего исполнителя родительской задачи — берем наименее загруженного, но нужно делать список
        if not candidates and least_loaded_employee:
            candidates.append(f"{get_full_name(least_loaded_employee)}")

        # Формирование выводных данных
        results.append({
            'important_task': task.title,
            'due_date': task.due_date,
            'available_employees': candidates,
        })

    return Response(results)


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    swagger_tags = ['Projects']


class PriorityViewSet(viewsets.ModelViewSet):
    queryset = Priority.objects.all()
    serializer_class = PrioritySerializer
    permission_classes = (IsAuthenticated, IsStaff)
    swagger_tags = ['Priorities']


class StatusViewSet(viewsets.ModelViewSet):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer
    permission_classes = (IsAuthenticated, IsStaff)
    swagger_tags = ['Statuses']


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    swagger_tags = ['Comments']


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated, IsOwner)
    swagger_tags = ['Tasks']

    def perform_create(self, serializer):
        """Метод делающий владельцем новой задачи текущего пользователя"""
        task = serializer.save()
        task.executor = self.request.user
        task.save()

    def perform_update(self, serializer):
        """Метод запускающий оповещение при изменении задачи"""
        updated_course = serializer.save()
        updated_course.save()
        # Здесь будет вызов функции оповещения
