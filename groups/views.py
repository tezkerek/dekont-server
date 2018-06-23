from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .permissions import IsInGroup, IsNotInGroup
from .serializers import GroupSerializer
from .models import Group

class GroupViewSet(viewsets.GenericViewSet):
    """
    A ViewSet for actions on groups.
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = GroupSerializer

    queryset = Group.objects.all()

    def get_permissions(self):
        permission_classes = [IsAuthenticated]

        if self.action == 'create':
            permission_classes.append(IsNotInGroup)

        return [permission() for permission in permission_classes]

    def create(self, request):
        # Validate and save
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group = serializer.save(group_admin=request.user)

        # Serialize and respond
        serializer = self.get_serializer(group)
        response_data = {'group': serializer.data}

        return Response(data=response_data, status=HTTP_201_CREATED)
