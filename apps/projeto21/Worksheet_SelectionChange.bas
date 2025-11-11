Attribute VB_Name = "Sheet_Dados_Code"
Option Explicit

' Coloque este módulo no "módulo de código" da planilha onde deseja o destaque.
' (Ao importar, mova o conteúdo para a planilha correta caso necessário)

Private Sub Worksheet_SelectionChange(ByVal Target As Range)
    On Error Resume Next
    Application.EnableEvents = False
    ThisWorkbook.Worksheets("Aux").Range("A1").Value = Target.Row
    Application.EnableEvents = True
End Sub
