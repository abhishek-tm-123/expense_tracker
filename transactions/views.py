from django.shortcuts import render,get_object_or_404

from rest_framework.views import APIView
from rest_framework import authentication,permissions
from rest_framework.response import Response

from transactions.models import Expense
from transactions.serializers import ExpenseSerializer
# Create your views here.

class ExpenseListCreateView(APIView):
    
    #authentication_classes = [authentication.BasicAuthentication]
    
    authentication_classes=[authentication.TokenAuthentication]
    
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
    
    #authentication_classes = [authentication.BasicAuthentication]
    
    authentication_classes=[authentication.TokenAuthentication]
    
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
    
    # authentication_classes = [authentication.BasicAuthentication]
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self,request):
        
        auth_user_expenses = Expense.objects.filter(owner=request.user)
        
        response_data = {
            "todays_total":0,
            "monthly_total":0
        }
        
        #todays
        cur_date = datetime.today().date()
        
        todays_total = auth_user_expenses.filter(created_at__date = cur_date).values("amount").aggregate(total=Sum("amount")).get("total")
        
        response_data["todays_total"] = todays_total
        
        #todays summary
        
        todays_summary = auth_user_expenses.filter(created_at__date = cur_date).values("category").annotate(total=Sum("amount"))
        
        response_data["todays_summary"] = todays_summary
        
        #monthly
        cur_month = datetime.today().month
        cur_year = datetime.today().year
        
        monthly_total = auth_user_expenses.filter(created_at__month=cur_month,created_at__year=cur_year).values("amount").aggregate(total=Sum("amount")).get("total")
        
        response_data["monthly_total"]=monthly_total
        
        #monthly summary
        
        monthly_summary = auth_user_expenses.filter(created_at__month=cur_month,created_at__year=cur_year).values("category").annotate(total=Sum("amount"))
        
        response_data["monthly_summary"] = monthly_summary
        
        return Response(response_data)
    
from rest_framework.parsers import MultiPartParser,FormParser
from rest_framework import status
from transactions.services import scan_bill

class BillScanView(APIView):

    authentication_classes=[authentication.TokenAuthentication]

    permission_classes = [permissions.IsAuthenticated]

    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):

        bill_image = request.FILES.get("bill_image")

        if not bill_image:
            return Response(
                {"error": "Please upload a bill image"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            data = scan_bill(bill_image)

            """
            "data":{"amount":1010.0,"category":"Bills","payment_method":null,"title":"Electricity Bill"}
            """
            serializer_instance = ExpenseSerializer(data=data)
            
            if serializer_instance.is_valid():
                
                serializer_instance.save(owner=request.user)
                
                return Response({
                                "message": "Bill scanned successfully",
                                "data": serializer_instance.data
                            })
            else:
                return Response(serializer_instance.errors)
                
            

        except Exception as e:

            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )