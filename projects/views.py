
from .models import Project
from projects.serializers import ProjectSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework import generics
from .filters import ProjectFilter
from django_filters.rest_framework import DjangoFilterBackend


@permission_classes((IsAuthenticatedOrReadOnly,))
class ProjectList(generics.ListAPIView):
    authentication_classes = (JSONWebTokenAuthentication,
                              SessionAuthentication)
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_class = ProjectFilter

    # def get_queryset(self):
    #     tag_name = self.request.query_params.get('tag_name', None)
    #     queryset = Project.objects.all()
    #     if tag_name is not None:
    #         queryset = queryset.filter(tags__name=tag_name)
    #     return queryset

    def get(self, request, format=None):
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ProjectSerializer(data=request.data)
        print(request.data)
        print(request.user.id)
        request.data['user'] = request.user.id
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes((IsAuthenticated,))
class ProjectDetail(APIView):
    authentication_classes = (JSONWebTokenAuthentication,
                              SessionAuthentication)

    def get_object(self, pk):
        try:
            return Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        project = self.get_object(pk)
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        project = self.get_object(pk=pk)
        serializer = ProjectSerializer(project, data=request.data)
        request.data['user'] = request.user.id
        if serializer.is_valid() and request.user == project.user:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        project = self.get_object(pk)
        if request.user == project.user:
            project.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
