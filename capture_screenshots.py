"""Genera capturas promocionales con datos ficticios de Factinxela."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PySide6.QtCore import QDate  # noqa: E402
from PySide6.QtWidgets import QApplication, QToolButton  # noqa: E402

from src.database import Database  # noqa: E402
from src.dialogs import RecordDialog, TemplateFieldsDialog  # noqa: E402
from src.main_window import MainWindow  # noqa: E402
from src.table_header import DateRangeDialog  # noqa: E402
from src.theme import APP_STYLE, FactinxelaStyle  # noqa: E402


OUTPUT = Path(__file__).resolve().parent / "assets" / "screenshots"


def _save_widget(widget, filename: str, application: QApplication) -> None:
    widget.show()
    application.processEvents()
    image = widget.grab()
    target = OUTPUT / filename
    if not image.save(str(target), "PNG"):
        raise RuntimeError(f"No se pudo guardar {target}")


def _configure_template(database: Database, template_id: int) -> None:
    associations = {
        "cliente": "{clientes.razon_social}",
        "nif": "{clientes.cif}",
        "direccion": (
            "{clientes.direccion_via}, {clientes.direccion_codigo_postal} "
            "{clientes.direccion_poblacion}"
        ),
        "fecha": "{facturas.fecha_factura}",
        "numero": "{facturas.serie_factura}-{facturas.num_factura}",
        "concepto": "{facturas.concepto}",
        "base": "{facturas.base_imponible}",
        "iva": "{facturas.iva_tipo_impositivo}",
        "total": "{facturas.total_factura}",
        "qr": "{facturas.url_qr}",
    }
    fields = database.template_fields(template_id)
    database.update_template_fields(
        template_id,
        {
            int(field["id"]): associations[str(field["nombre_campo"])]
            for field in fields
        },
    )


def _seed_database(database: Database, directory: Path) -> tuple[int, int]:
    database.initialize()
    issuer_id = database.insert(
        "emisores",
        {
            "tipo_persona": "Persona física",
            "razon_social": "Ana Vega García",
            "cif": "12345678Z",
            "telefono": "600 123 456",
            "email": "ana@ejemplo.test",
            "serie_factura": "F2026",
            "num_factura_init": 101,
            "direccion_via": "Calle del Mercado, 12",
            "direccion_codigo_postal": "28004",
            "direccion_poblacion": "Madrid",
            "direccion_provincia": "Madrid",
            "direccion_pais": "España",
        },
    )
    second_issuer_id = database.insert(
        "emisores",
        {
            "tipo_persona": "Persona física",
            "razon_social": "Bruno López Ruiz",
            "cif": "87654321X",
            "serie_factura": "B2026",
            "num_factura_init": 45,
            "direccion_poblacion": "Valencia",
            "direccion_pais": "España",
        },
    )

    field_names = (
        "cliente",
        "nif",
        "direccion",
        "fecha",
        "numero",
        "concepto",
        "base",
        "iva",
        "total",
        "qr",
    )
    template_directory = Path("C:/Factinxela/Plantillas")
    professional_template = database.create_template(
        template_directory / "Factura profesional.pdf",
        field_names,
        irpf_rate=15,
        iva_rate=21,
    )
    services_template = database.create_template(
        template_directory / "Factura servicios.pdf",
        field_names,
        irpf_rate=0,
        iva_rate=21,
    )
    _configure_template(database, professional_template)
    _configure_template(database, services_template)

    clients = [
        (
            "Clínica Horizonte SL",
            "B12345670",
            professional_template,
            "CLINICA-HORIZONTE",
            "Paseo de la Salud, 18",
            "28010",
            "Madrid",
        ),
        (
            "Estudio Nébula",
            "B76543210",
            services_template,
            "NEBULA",
            "Calle Luna, 7",
            "46001",
            "Valencia",
        ),
        (
            "Centro Albor",
            "B11223344",
            professional_template,
            "ALBOR",
            "Avenida Norte, 42",
            "48009",
            "Bilbao",
        ),
        (
            "Cooperativa Brisa",
            "F55667788",
            services_template,
            "BRISA",
            "Rúa Nova, 15",
            "15003",
            "A Coruña",
        ),
        (
            "Taller Lumen",
            "B99887766",
            services_template,
            "LUMEN",
            "Calle Taller, 3",
            "41003",
            "Sevilla",
        ),
    ]
    client_ids: list[int] = []
    for name, cif, template_id, identifier, address, postal_code, city in clients:
        client_ids.append(
            database.insert(
                "clientes",
                {
                    "tipo_persona": "Persona jurídica",
                    "razon_social": name,
                    "cif": cif,
                    "email": f"hola@{identifier.lower()}.test",
                    "plantilla_id": template_id,
                    "identificador": identifier,
                    "direccion_via": address,
                    "direccion_codigo_postal": postal_code,
                    "direccion_poblacion": city,
                    "direccion_provincia": city,
                    "direccion_pais": "España",
                },
            )
        )

    shipment_ok = database.insert(
        "envios_agencia",
        {
            "csv": "CSV-DEMO-2026-00041",
            "timestamp_presentacion": "2026-07-28T10:32:18+02:00",
            "tiempo_espera_envio": 60,
            "estado_envio": "Correcto",
        },
    )
    shipment_warning = database.insert(
        "envios_agencia",
        {
            "csv": "CSV-DEMO-2026-00042",
            "timestamp_presentacion": "2026-07-28T11:04:05+02:00",
            "tiempo_espera_envio": 60,
            "estado_envio": "ParcialmenteCorrecto",
        },
    )
    common_url = (
        "https://prewww2.aeat.es/wlpl/TIKE-CONT/ValidarQR?"
        "nif=12345678Z&numserie=F2026-"
    )
    invoices = [
        {
            "estado": "Aceptada",
            "emisor_id": issuer_id,
            "fecha_factura": "2026-07-24",
            "serie_factura": "F2026",
            "num_factura": 101,
            "cliente_id": client_ids[0],
            "concepto": "Servicios profesionales de julio",
            "base_imponible": 850,
            "irpf_tipo_retencion": 15,
            "iva_tipo_impositivo": 21,
            "total_factura": 901,
            "url_qr": f"{common_url}101&fecha=24-07-2026&importe=1028.50",
            "huella": "A" * 64,
            "fecha_hora_huso_gen_registro": "2026-07-28T10:31:44+02:00",
            "envios_agencia_id": shipment_ok,
        },
        {
            "estado": "Aceptada",
            "emisor_id": issuer_id,
            "fecha_factura": "2026-07-25",
            "serie_factura": "F2026",
            "num_factura": 102,
            "cliente_id": client_ids[1],
            "concepto": "Diseño y consultoría",
            "base_imponible": 620,
            "irpf_tipo_retencion": 0,
            "iva_tipo_impositivo": 21,
            "total_factura": 750.2,
            "url_qr": f"{common_url}102&fecha=25-07-2026&importe=750.20",
            "huella": "B" * 64,
            "fecha_hora_huso_gen_registro": "2026-07-28T10:31:44+02:00",
            "envios_agencia_id": shipment_ok,
        },
        {
            "estado": "Aceptada con errores",
            "emisor_id": issuer_id,
            "fecha_factura": "2026-07-26",
            "serie_factura": "F2026",
            "num_factura": 103,
            "cliente_id": client_ids[2],
            "concepto": "Sesiones y seguimiento",
            "base_imponible": 480,
            "irpf_tipo_retencion": 15,
            "iva_tipo_impositivo": 21,
            "total_factura": 508.8,
            "url_qr": f"{common_url}103&fecha=26-07-2026&importe=580.80",
            "huella": "C" * 64,
            "fecha_hora_huso_gen_registro": "2026-07-28T11:03:40+02:00",
            "envios_agencia_id": shipment_warning,
            "errores_aeat": "2000 - Registro aceptado con observaciones",
        },
        {
            "estado": "Borrador",
            "emisor_id": issuer_id,
            "fecha_factura": "2026-07-28",
            "cliente_id": client_ids[3],
            "concepto": "Mantenimiento mensual",
            "base_imponible": 300,
            "irpf_tipo_retencion": 0,
            "iva_tipo_impositivo": 21,
            "total_factura": 363,
        },
        {
            "estado": "Incorrecta",
            "emisor_id": second_issuer_id,
            "fecha_factura": "2026-07-28",
            "serie_factura": "B2026",
            "num_factura": 45,
            "cliente_id": client_ids[4],
            "concepto": "Asistencia técnica",
            "base_imponible": 210,
            "irpf_tipo_retencion": 0,
            "iva_tipo_impositivo": 21,
            "total_factura": 254.1,
            "huella": "D" * 64,
            "fecha_hora_huso_gen_registro": "2026-07-28T11:18:12+02:00",
            "envios_agencia_id": shipment_warning,
            "errores_aeat": "4102 - El registro contiene datos que deben revisarse",
        },
    ]
    for invoice in invoices:
        database.insert("facturas", invoice)
    return issuer_id, professional_template


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    application = QApplication.instance() or QApplication([])
    application.setApplicationName("Factinxela")
    application.setStyle(FactinxelaStyle("Fusion"))
    application.setStyleSheet(APP_STYLE)

    with tempfile.TemporaryDirectory(prefix="factinxela-web-") as temporary:
        directory = Path(temporary)
        database = Database(directory / "factinxela_demo.db")
        issuer_id, template_id = _seed_database(database, directory)

        window = MainWindow(database)
        window.resize(1500, 920)
        _save_widget(window, "01-panel-principal.png", application)

        window.show_table("facturas")
        application.processEvents()
        _save_widget(window, "02-facturas.png", application)

        window.show_table("plantillas")
        application.processEvents()
        _save_widget(window, "03-plantillas.png", application)

        template_dialog = TemplateFieldsDialog(database, template_id)
        template_dialog.resize(1280, 760)
        _save_widget(
            template_dialog,
            "04-configuracion-plantilla.png",
            application,
        )
        template_dialog.close()

        date_dialog = DateRangeDialog("2026-07-24", "2026-07-28")
        date_dialog.resize(540, 370)
        _save_widget(date_dialog, "05-filtro-fechas.png", application)
        date_dialog.close()

        issuer = database.fetch_one("emisores", issuer_id)
        issuer_dialog = RecordDialog(database, "emisores", issuer)
        issuer_dialog.resize(920, 760)
        help_button = issuer_dialog.findChild(
            QToolButton, "issuerSeriesHelpButton"
        )
        _save_widget(issuer_dialog, "06-emisor.png", application)
        if help_button is not None:
            issuer_dialog._show_series_help(help_button)
            application.processEvents()
            if issuer_dialog._series_help_popup is not None:
                _save_widget(
                    issuer_dialog._series_help_popup,
                    "07-ayuda-serie.png",
                    application,
                )
                issuer_dialog._series_help_popup.close()
        issuer_dialog.close()
        window.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
