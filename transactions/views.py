from django.shortcuts import render,get_object_or_404

from rest_framework.views import APIView
from rest_framework import authentication,permissions
from rest_framework.response import Response

from transactions.models import Expense
from transactions.serializers import ExpenseSerializer
# Create your views here.

class ExpenseListCreateView(APIView):
    
    authentication_classes = [authentication.BasicAuthentication]
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self,request):
        
        auth_user = request.user
        
        qs = Expense.objects.filter(owner=auth_user)
        
        serializer_instance = ExpenseSerializer(qs,many=True)
        
        return Response(serializer_instance.data)
    
    def post(self,request):
        
        form_data = request.data
        
        auth_user = request.user
        
        serializer_instance = ExpenseSerializer(data=form_data)
        
        if serializer_instance.is_valid():
            
            serializer_instance.save(owner=auth_user)
            
            return Response(serializer_instance.data)
        else:
            return Response(serializer_instance.errors)
        
from transactions.permissions import IsOwner
        
class ExpenseRetreiveUpdateDeleteView(APIView):
    
    authentication_classes = [authentication.BasicAuthentication]
    
    permission_classes = [IsOwner]
    
    def get(self,request,pk=None):
        
        qs = get_object_or_404(Expense,id = pk)
        
        self.check_object_permissions(request,qs)
        
        serializer_instance = ExpenseSerializer(qs)
        
        return Response(serializer_instance.data)
    
    def put(self,request,pk=None):
        
        instance = get_object_or_404(Expense,id=pk)
        
        self.check_object_permissions(request,instance)
        
        form_data = request.data
        
        serialaizer_instance = ExpenseSerializer(data=form_data,instance=instance)
        
        if serialaizer_instance.is_valid():
            serialaizer_instance.save()
        
            return Response(serialaizer_instance.data)
        else:
            return Response(serialaizer_instance.errors)
    
    def delete(self,request,pk=None):
        instance = get_object_or_404(Expense,id=pk)
        self.check_object_permissions(request,instance)
        instance.delete()
        return Response({"message":"deleted....."})
    
from datetime import datetime
from django.db.models import Sum
    
class ExpenseSummaryView(APIView):
    
    authentication_classes = [authentication.BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self,request):
        
        auth_user_expenses = Expense.objects.filter(id=request.user)
        
        response_data = {
            "todays_total":0,
            "monthly_total":0
        }
        
        cur_date = datetime.today().date()
        
        todays_total = auth_user_expenses.filter(created_at__date = cur_date).values("amount").aggregate(total=Sum("amount")).get("total")
        
        response_data["todays_total"] = todays_total
        
        return Response(response_data)