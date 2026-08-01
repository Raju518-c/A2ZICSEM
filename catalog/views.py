from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FormField, FormModule, ReferenceValue, ScopeCatalog, ScopeModule
from .serializers import (
    FormFieldSerializer,
    FormModuleSerializer,
    ReferenceValueSerializer,
    ScopeCatalogSerializer,
    ScopeModuleSerializer,
)


class ReferenceValueListCreateAPIView(APIView):
    """
    GET  : Get all reference values
    POST : Create a new reference value
    """

    permission_classes = [AllowAny]

    def get(self, request):
        reference_values = ReferenceValue.objects.all().order_by(
            "option_set", "sort_order", "label"
        )
        serializer = ReferenceValueSerializer(reference_values, many=True)

        return Response(
            {
                "success": True,
                "message": "Reference values fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = ReferenceValueSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Reference value created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class ReferenceValueRetrieveUpdateDeleteAPIView(APIView):
    """
    GET    : Get reference value by ID
    PUT    : Update reference value (partial)
    DELETE : Delete reference value
    """

    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return ReferenceValue.objects.get(pk=pk)
        except ReferenceValue.DoesNotExist:
            return None

    def get(self, request, pk):
        reference_value = self.get_object(pk)

        if not reference_value:
            return Response(
                {
                    "success": False,
                    "message": "Reference value not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ReferenceValueSerializer(reference_value)

        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        reference_value = self.get_object(pk)

        if not reference_value:
            return Response(
                {
                    "success": False,
                    "message": "Reference value not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ReferenceValueSerializer(
            reference_value, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Reference value updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        reference_value = self.get_object(pk)

        if not reference_value:
            return Response(
                {
                    "success": False,
                    "message": "Reference value not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        reference_value.delete()

        return Response(
            {
                "success": True,
                "message": "Reference value deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )


class ScopeCatalogListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        scope_catalogs = ScopeCatalog.objects.all().order_by("industry", "scope_name")
        serializer = ScopeCatalogSerializer(scope_catalogs, many=True)
        return Response(
            {"success": True, "message": "Scope catalogs fetched successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = ScopeCatalogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Scope catalog created successfully.", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ScopeCatalogRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return ScopeCatalog.objects.get(pk=pk)
        except ScopeCatalog.DoesNotExist:
            return None

    def get(self, request, pk):
        scope_catalog = self.get_object(pk)
        if not scope_catalog:
            return Response({"success": False, "message": "Scope catalog not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ScopeCatalogSerializer(scope_catalog)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, pk):
        scope_catalog = self.get_object(pk)
        if not scope_catalog:
            return Response({"success": False, "message": "Scope catalog not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ScopeCatalogSerializer(scope_catalog, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Scope catalog updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        scope_catalog = self.get_object(pk)
        if not scope_catalog:
            return Response({"success": False, "message": "Scope catalog not found."}, status=status.HTTP_404_NOT_FOUND)
        scope_catalog.delete()
        return Response({"success": True, "message": "Scope catalog deleted successfully."}, status=status.HTTP_200_OK)


class FormModuleListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        form_modules = FormModule.objects.all().order_by("module_code", "version")
        serializer = FormModuleSerializer(form_modules, many=True)
        return Response(
            {"success": True, "message": "Form modules fetched successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = FormModuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Form module created successfully.", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class FormModuleRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return FormModule.objects.get(pk=pk)
        except FormModule.DoesNotExist:
            return None

    def get(self, request, pk):
        form_module = self.get_object(pk)
        if not form_module:
            return Response({"success": False, "message": "Form module not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = FormModuleSerializer(form_module)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, pk):
        form_module = self.get_object(pk)
        if not form_module:
            return Response({"success": False, "message": "Form module not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = FormModuleSerializer(form_module, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Form module updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        form_module = self.get_object(pk)
        if not form_module:
            return Response({"success": False, "message": "Form module not found."}, status=status.HTTP_404_NOT_FOUND)
        form_module.delete()
        return Response({"success": True, "message": "Form module deleted successfully."}, status=status.HTTP_200_OK)


class ScopeModuleListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        scope_modules = ScopeModule.objects.all().order_by("scope", "sequence")
        serializer = ScopeModuleSerializer(scope_modules, many=True)
        return Response(
            {"success": True, "message": "Scope modules fetched successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = ScopeModuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Scope module created successfully.", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ScopeModuleRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return ScopeModule.objects.get(pk=pk)
        except ScopeModule.DoesNotExist:
            return None

    def get(self, request, pk):
        scope_module = self.get_object(pk)
        if not scope_module:
            return Response({"success": False, "message": "Scope module not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ScopeModuleSerializer(scope_module)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, pk):
        scope_module = self.get_object(pk)
        if not scope_module:
            return Response({"success": False, "message": "Scope module not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ScopeModuleSerializer(scope_module, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Scope module updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        scope_module = self.get_object(pk)
        if not scope_module:
            return Response({"success": False, "message": "Scope module not found."}, status=status.HTTP_404_NOT_FOUND)
        scope_module.delete()
        return Response({"success": True, "message": "Scope module deleted successfully."}, status=status.HTTP_200_OK)


class FormFieldListCreateAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        form_fields = FormField.objects.all().order_by("form_module", "sequence")
        serializer = FormFieldSerializer(form_fields, many=True)
        return Response(
            {"success": True, "message": "Form fields fetched successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = FormFieldSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": True, "message": "Form field created successfully.", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class FormFieldRetrieveUpdateDeleteAPIView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return FormField.objects.get(pk=pk)
        except FormField.DoesNotExist:
            return None

    def get(self, request, pk):
        form_field = self.get_object(pk)
        if not form_field:
            return Response({"success": False, "message": "Form field not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = FormFieldSerializer(form_field)
        return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, pk):
        form_field = self.get_object(pk)
        if not form_field:
            return Response({"success": False, "message": "Form field not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = FormFieldSerializer(form_field, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "message": "Form field updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        form_field = self.get_object(pk)
        if not form_field:
            return Response({"success": False, "message": "Form field not found."}, status=status.HTTP_404_NOT_FOUND)
        form_field.delete()
        return Response({"success": True, "message": "Form field deleted successfully."}, status=status.HTTP_200_OK)

