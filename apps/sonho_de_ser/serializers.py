from rest_framework import serializers

from .models import (
    AnotacaoMentor,
    Area,
    Estrategia,
    MentorProfile,
    Mentoria,
    RegistroDiario,
)


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ["id", "inicial", "nome"]


class EstrategiaSerializer(serializers.ModelSerializer):
    area = AreaSerializer(read_only=True)
    nivel_label = serializers.CharField(source="get_nivel_display", read_only=True)

    class Meta:
        model = Estrategia
        fields = [
            "id",
            "titulo",
            "codigo",
            "descricao",
            "nivel",
            "nivel_label",
            "ordem_nivel",
            "dificuldade",
            "pontos",
            "ativo",
            "area",
        ]


class RegistroDiarioSerializer(serializers.ModelSerializer):
    estrategia = EstrategiaSerializer(read_only=True)
    codigo = serializers.CharField(write_only=True, required=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = RegistroDiario
        fields = [
            "id",
            "data",
            "codigo",
            "status",
            "status_label",
            "observacao",
            "estrategia",
        ]

    def create(self, validated_data):
        request = self.context["request"]
        codigo = validated_data.pop("codigo")

        try:
            estrategia = Estrategia.objects.get(codigo=codigo, ativo=True)
        except Estrategia.DoesNotExist as exc:
            raise serializers.ValidationError({"codigo": "Estrategia invalida."}) from exc

        return RegistroDiario.objects.create(
            usuario=request.user,
            estrategia=estrategia,
            **validated_data,
        )


class MentorProfileSerializer(serializers.ModelSerializer):
    usuario_email = serializers.EmailField(source="usuario.email", read_only=True)

    class Meta:
        model = MentorProfile
        fields = ["id", "usuario_email", "papel"]


class MentoriaSerializer(serializers.ModelSerializer):
    mentor_email = serializers.EmailField(source="mentor.email", read_only=True)
    mentorado_email = serializers.EmailField(source="mentorado.email", read_only=True)

    class Meta:
        model = Mentoria
        fields = [
            "id",
            "mentor",
            "mentorado",
            "mentor_email",
            "mentorado_email",
            "status",
            "ativo",
            "escopo",
            "pode_ver_registros",
            "pode_criar_anotacoes",
            "observacoes",
            "criado_em",
            "consentido_em",
            "aceita_pelo_mentorado_em",
            "revogada_em",
        ]
        read_only_fields = [
            "mentor_email",
            "mentorado_email",
            "criado_em",
            "consentido_em",
            "aceita_pelo_mentorado_em",
            "revogada_em",
        ]


class AnotacaoMentorSerializer(serializers.ModelSerializer):
    mentor_email = serializers.EmailField(source="mentoria.mentor.email", read_only=True)

    class Meta:
        model = AnotacaoMentor
        fields = [
            "id",
            "mentoria",
            "mentor_email",
            "texto",
            "visivel_para_aluno",
            "data",
            "created_at",
        ]
        read_only_fields = ["mentor_email", "data", "created_at"]
