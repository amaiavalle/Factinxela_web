# Web de Factinxela

Página promocional estática y sin dependencias externas.

## Verla en local

Abre `index.html` directamente en el navegador. También puede publicarse copiando todo el contenido de esta carpeta a cualquier alojamiento de archivos estáticos.

## Archivos

- `index.html`: estructura y contenidos.
- `styles.css`: diseño responsive, animaciones y estilos de impresión visual.
- `app.js`: menú móvil, animaciones y galería ampliable.
- `assets/screenshots/`: capturas reales de la aplicación con datos ficticios.
- `capture_screenshots.py`: generador reproducible de las capturas. Crea una base temporal y no accede a los datos reales de Factinxela.

Para regenerar las capturas en Windows:

```powershell
$env:QT_QPA_PLATFORM='windows'
python web\capture_screenshots.py
```
