import django.db
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from delivery.models import Courier, Order
from delivery.serializers import CourierSerializer, OrderSerializer

from datetime import datetime


def get_time_now():
    return str(datetime.now().date()) + 'T' + str(datetime.now().time())[:11] + 'Z'


class CouriersList(APIView):
    def get(self, request, format=None):
        couriers = Courier.objects.all()
        serializer = CourierSerializer(couriers, many=True)
        return JsonResponse(serializer.data, safe=False)

    def post(self, request, format=None):
        data = JSONParser().parse(request)
        errors = []
        created = []
        if not bool(data.get("data", None)):
            return HttpResponse(status=400)
        for courier in data["data"]:
            serializer = CourierSerializer(data=courier)
            if serializer.is_valid():
                serializer.save()
                created.append({"id": courier["courier_id"]})
            else:
                errors.append({"id": courier.get("courier_id", None)})
        if not errors:
            return JsonResponse(
                {
                    "couriers": created
                }, status=201
            )
        else:
            return JsonResponse(
                {
                    "validation_error": {
                        "couriers": errors
                    }
                },
                status=400
            )


class CourierDetail(APIView):

    def get_object(self, pk):
        try:
            return Courier.objects.get(pk=pk)
        except Courier.DoesNotExist as e:
            raise Http404

    def get(self, request, pk, format=None):
        courier = self.get_object(pk)
        serializer = CourierSerializer(courier)
        return JsonResponse(serializer.data)

    def patch(self, request, pk, format=None):
        courier = self.get_object(pk)
        data = JSONParser().parse(request)
        serializer = CourierSerializer(courier, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            had_orders = False
            for order in courier.order_set.all().filter(complete_time=None):
                had_orders = True
                is_intersect = False
                for d1 in order.delivery_hours:
                    for d2 in courier.working_hours:
                        is_intersect = is_intersect or time_ranges_intersect(d1, d2)
                if not is_intersect or order.region not in courier.regions:
                    order.courier = None
                    order.save()
            orders = courier.order_set.all().filter(complete_time=None)
            if not orders and had_orders:
                Courier.update_courier_earnings(courier)
            return JsonResponse(serializer.data, status=200)
        return JsonResponse(serializer.errors, status=400)

    def delete(self, request, pk, format=None):
        courier = self.get_object(pk)
        courier.delete()
        return HttpResponse(204)


class OrdersList(APIView):
    def get(self):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return JsonResponse(serializer.data, safe=False)

    def post(self, request, format=None):
        data = JSONParser().parse(request)
        created = []
        errors = []
        if not bool(data.get("data", None)):
            return HttpResponse(status=400)
        for order in data["data"]:
            serializer = OrderSerializer(data=order)
            if serializer.is_valid():
                created.append({"id": order["order_id"]})
                serializer.save()
            else:
                errors.append({"id": order.get("order_id", None)})
        if errors:
            return JsonResponse(
                {
                    "validation_error": {
                        "orders": errors
                    }
                },
                status=400
            )
        return JsonResponse(
            {
                "orders": created
            },
            status=201
        )


def time_ranges_intersect(time_range1, time_range2):
    tl1, tr1 = time_range1.split("-")
    tl2, tr2 = time_range2.split("-")
    tl1, tr1 = tl1.split(':'), tr1.split(':')
    tl2, tr2 = tl2.split(':'), tr2.split(':')
    tl1 = int(tl1[0]) * 60 + int(tl1[1])
    tr1 = int(tr1[0]) * 60 + int(tr1[1])
    tl2 = int(tl2[0]) * 60 + int(tl2[1])
    tr2 = int(tr2[0]) * 60 + int(tr2[1])
    if tr2 <= tl1 or tr1 <= tl2:
        return False
    return True


class OrderAssign(APIView):
    max_weight = {
        'foot': 10,
        'bike': 15,
        'car': 50
    }

    def post(self, request):
        data = JSONParser().parse(request)
        if data.get("courier_id", None) is None:
            return HttpResponse(status=400)
        try:
            courier = Courier.objects.get(pk=data["courier_id"])
        except Courier.DoesNotExist as e:
            return HttpResponse(status=400)

        old_orders = Order.objects.filter(courier=courier, complete_time=None)
        answer = list(map(lambda order: {"id": order.order_id}, old_orders))
        if old_orders:
            return JsonResponse(
                {
                    "orders": answer,
                    "assign_time": courier.assign_time
                },
                status=200
            )

        new_orders_raw = Order.objects.filter(
            courier=None,
            region__in=courier.regions,
            weight__lte=self.max_weight[courier.courier_type]
        )

        new_orders = []
        for order in new_orders_raw:
            is_intersect = False
            for d1 in order.delivery_hours:
                for d2 in courier.working_hours:
                    is_intersect = is_intersect or time_ranges_intersect(d1, d2)
            if is_intersect:
                new_orders.append(order)

        if new_orders:
            courier.assign_time = get_time_now()
            courier.save()
            for order in new_orders:
                order.courier = courier
                order.save()
                answer.append({"id": order.order_id})
        if answer:
            return JsonResponse(
                {
                    "orders": answer,
                    "assign_time": courier.assign_time
                },
                status=200
            )
        return JsonResponse({"orders": []}, status=200)


class OrderComplete(APIView):

    def post(self, request):
        data = JSONParser().parse(request)
        if not all(map(bool, [data["courier_id"], data["order_id"], data["complete_time"]])):
            return HttpResponse(status=400)
        try:
            order = Order.objects.get(pk=data["order_id"])
        except Order.DoesNotExist as e:
            return HttpResponse(status=400)
        if order.courier is None or order.courier.courier_id != data["courier_id"]:
            return HttpResponse(status=400)

        order.complete_time = data["complete_time"]
        order.save()
        orders = order.courier.order_set.all().filter(complete_time=None)
        if not orders:
            Courier.update_courier_earnings(order.courier)
        return JsonResponse({"order_id": order.order_id}, status=200)
