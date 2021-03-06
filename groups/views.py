from django.shortcuts import get_object_or_404, redirect
from rest_framework import viewsets, mixins
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED

from .permissions import IsInGroup, IsNotInAnyGroup
from .serializers import GroupSerializer
from .models import Group

class GroupViewSet(mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   viewsets.GenericViewSet):
    """
    A ViewSet for actions on groups.
    """
    serializer_class = GroupSerializer
    permission_classes = (IsAuthenticated,)
    per_action_permission_classes = {
        'create': {
            'post': permission_classes + (IsNotInAnyGroup,)
        },
        'update': {
            'put': permission_classes + (IsInGroup,)
        },
        'partial_update': {
            'patch': permission_classes + (IsInGroup,)
        }
    }

    def get_queryset(self):
        # Single-element list containing the user's group.
        user = self.request.user
        return Group.objects.filter(pk=user.group_id)

    def get_permissions(self):
        per_action_permission_classes = getattr(self, 'per_action_permission_classes', {})

        # Get the permissions classes for the action and method,
        # or the default ones if not defined.
        permission_classes = per_action_permission_classes \
            .get(self.action, {}) \
            .get(self.request.method.lower(), self.permission_classes)

        return [permission() for permission in permission_classes]

    def get_serializer_context(self):
        return {
            'request': self.request,
            'action': self.action
        }

    def create(self, request):
        # Validate and save
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group = serializer.save(group_admin=request.user)

        # Serialize and respond
        serializer = self.get_serializer(group)
        response_data = {'group': serializer.data}

        return Response(data=response_data, status=HTTP_201_CREATED)

class CurrentUserGroup(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        return redirect('group-detail', pk=request.user.group_id)

current_user_group = CurrentUserGroup.as_view()
