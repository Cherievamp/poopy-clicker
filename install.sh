#!/usr/bin/env bash
set -euo pipefail

NAME="Poopy Clicker"
CMD="poopy-clicker"
APP_DIR="/opt/$CMD"
VENV_DIR="$APP_DIR/venv"
BIN_LINK="/usr/local/bin/$CMD"
DESKTOP_FILE="/usr/share/applications/$CMD.desktop"
ICON_DIR="/usr/share/icons/hicolor/128x128/apps"

if [ "$(id -u)" -ne 0 ]; then
    echo "Execute como root: sudo ./install.sh"
    exit 1
fi

echo "🔧 Instalando $NAME..."

if ! command -v python3 &>/dev/null; then
    echo "❌ Python 3 não encontrado. Instale python3 primeiro."
    exit 1
fi

if ! python3 -c "import venv" &>/dev/null; then
    echo "❌ Módulo venv não encontrado. Instale python3-venv."
    exit 1
fi

echo "📁 Criando diretórios..."
mkdir -p "$APP_DIR" "$ICON_DIR"

echo "📦 Criando ambiente virtual..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo "📥 Instalando dependências..."
pip install --upgrade pip
pip install .

echo "🔗 Criando atalho $BIN_LINK..."
cat > "$BIN_LINK" << 'SCRIPT'
#!/usr/bin/env bash
exec /opt/poopy-clicker/venv/bin/python -m poopy_clicker
SCRIPT
chmod +x "$BIN_LINK"

echo "🖼️ Instalando ícone..."
if [ -f "poopy_clicker/assets/Algo.png" ]; then
    cp "poopy_clicker/assets/Algo.png" "$ICON_DIR/poopy-clicker.png"
fi

echo "📝 Instalando atalho de menu..."
cat > "$DESKTOP_FILE" << DESKTOP
[Desktop Entry]
Type=Application
Name=$NAME
Comment=Jogo de cliques com goobers
Exec=$CMD
Icon=poopy-clicker
Terminal=false
Categories=Game;
DESKTOP

echo "💀 Atualizando cache de ícones..."
gtk-update-icon-cache -f /usr/share/icons/hicolor/ 2>/dev/null || true

echo ""
echo "✅ $NAME instalado!"
echo "   Rode '$CMD' no terminal ou procure no menu de apps."
