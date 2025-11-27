from rest_framework import serializers
from .models import (
    Area,
    Estrategia,
    RegistroDiario,
    MentorProfile,
    Mentoria,
    AnotacaoMentor,
)


# -------------------
#   ÁREA
# -------------------
class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ["id", "inicial", "nome"]


# -------------------
#   ESTRATÉGIA
# -------------------
class EstrategiaSerializer(serializers.ModelSerializer):
    area = AreaSerializer(read_only=True)

    class Meta:
        model = Estrategia
        fields = [
            "id", "titulo", "codigo", "descricao",
            "nivel", "ordem_nivel",
            "dificuldade", "pontos", "ativo",
            "area",
        ]

# -------------------
#   REGISTRO DIÁRIO
# -------------------
class RegistroDiarioSerializer(serializers.ModelSerializer):
    estrategia = EstrategiaSerializer(read_only=True)
    codigo = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = RegistroDiario
        fields = [
            "id",
            "data",
            "concluido",
            "nota",
            "observacao",
            "codigo",       # write_only para criar via código
            "estrategia",   # read_only
        ]

    def create(self, validated_data):
        request = self.context["request"]
        codigo = validated_data.pop("codigo")

        try:
            est = Estrategia.objects.get(codigo=codigo, ativo=True)
        except Estrategia.DoesNotExist:
            raise serializers.ValidationError({"codigo": "Estratégia inválida."})

        reg = RegistroDiario.objects.create(
            usuario=request.user,
            estrategia=est,
            **validated_data,
        )
        return reg


# -------------------
#   MENTOR PROFILE
# -------------------
class MentorProfileSerializer(serializers.ModelSerializer):
    usuario_email = serializers.EmailField(source="usuario.email", read_only=True)

    class Meta:
        model = MentorProfile
        fields = ["id", "usuario_email", "bio", "telefone", "ativo", "criado_em"]


# -------------------
#   MENTORIA
# -------------------
class MentoriaSerializer(serializers.ModelSerializer):
    mentor_email = serializers.EmailField(source="mentor.usuario.email", read_only=True)
    aluno_email = serializers.EmailField(source="aluno.email", read_only=True)

    class Meta:
        model = Mentoria
        fields = [
            "id",
            "mentor_email",
            "aluno_email",
            "status",
            "inicio",
            "fim",
            "notas",
            "criado_em",
            "atualizado_em",
        ]


# -------------------
#   ANOTAÇÃO DE MENTOR
# -------------------
class AnotacaoMentorSerializer(serializers.ModelSerializer):
    autor_email = serializers.EmailField(source="autor.usuario.email", read_only=True)

    class Meta:
        model = AnotacaoMentor
        fields = [
            "id",
            "mentoria",
            "autor_email",
            "texto",
            "visibilidade",
            "data",
            "criado_em",
        ]
