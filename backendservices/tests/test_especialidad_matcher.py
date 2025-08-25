from app.services.especialidad_matcher import asignar_especialidad

def test_asignar_especialidad():
    especialidades = [
        {"especialidad": "Tráfico Aéreo", "pagina": 10},
        {"especialidad": "Planeación Aeroportuaria", "pagina": 20},
        {"especialidad": "Ingeniería Aeronáutica", "pagina": 30}
    ]

    casos = [
        (9, "Desconocida"),
        (10, "Tráfico Aéreo"),
        (15, "Tráfico Aéreo"),
        (20, "Planeación Aeroportuaria"),
        (29, "Planeación Aeroportuaria"),
        (30, "Ingeniería Aeronáutica"),
        (50, "Ingeniería Aeronáutica")
    ]

    for pagina, esperado in casos:
        resultado = asignar_especialidad(pagina, especialidades)
        print(f"Página {pagina}: → {resultado}")
        assert resultado == esperado, f"❌ Error en página {pagina}: esperado {esperado}, obtenido {resultado}"
    print("✅ Todos los tests pasaron correctamente.")

if __name__ == "__main__":
    test_asignar_especialidad()