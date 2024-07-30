from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .util import create_meet_space


class MeetSpaceAPIView(APIView):
    def get(self, request):
        meet_space_name = create_meet_space()
        if meet_space_name:
            return Response({'meet_space_name': meet_space_name}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Failed to create Meet space'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
