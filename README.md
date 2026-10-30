# RSS a Telegram

Publica automáticamente las noticias de varios feeds RSS en el canal de Telegram **@ElPatriarcaFEED**, con el título en una línea y el enlace debajo (Telegram genera la vista previa). Funciona gratis con GitHub Actions y un bot propio de Telegram; sustituye a IFTTT.

Se ejecuta cada 5 minutos gracias a una tarea de [cron-job.org](https://console.cron-job.org/jobs) que pulsa «Run workflow» mediante la API de GitHub (token de grano fino «cron-job rss-telegram», solo con permiso de Actions sobre este repositorio y sin caducidad). El programador propio de GitHub (`cron` en `rss.yml`) se mantiene como respaldo. El aviso de la API indica que la versión 2022-11-28 deja de funcionar el 10/03/2028: antes de esa fecha hay que añadir en cron-job.org la cabecera `X-GitHub-Api-Version` con la versión vigente.

## Añadir o quitar un sitio

1. Abre `feeds.txt` en GitHub y pulsa el lápiz (✏️) para editarlo.
2. Añade la dirección del feed en una línea nueva. En webs WordPress suele bastar con añadir `/feed/` al final de la dirección.
3. Pulsa **Commit changes**.

Un feed nuevo se registra en la siguiente ejecución sin publicar nada antiguo; a partir de ahí se publican solo las noticias nuevas. Para quitar un sitio, borra su línea. Las líneas que empiezan por `#` se ignoran.

## Ejecutarlo a mano

Pestaña **Actions** → **RSS a Telegram** → **Run workflow** → **Run workflow**.

## Si GitHub pausa el workflow

GitHub desactiva los workflows programados de los repositorios públicos tras 60 días sin actividad. Si deja de publicar:

1. Ve a **Actions** → **RSS a Telegram**.
2. Si aparece un aviso de que está desactivado, pulsa **Enable workflow**.
3. Lánzalo una vez a mano con **Run workflow** para comprobar que funciona.

## Configuración (Secrets)

En **Settings → Secrets and variables → Actions**:

- `TELEGRAM_TOKEN`: el token del bot que da @BotFather.
- `TELEGRAM_CHAT_ID`: `@ElPatriarcaFEED`

El bot tiene que ser administrador del canal con permiso para publicar mensajes.

## Archivos

- `feeds.txt`: lista de feeds.
- `rss_telegram.py`: el script que lee los feeds y publica.
- `seen.json`: noticias ya publicadas (lo actualiza el propio workflow; no hace falta tocarlo).
- `.github/workflows/rss.yml`: la programación en GitHub Actions.
