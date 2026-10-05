"""Uso: python scripts/check_robots.py <https://sitio.com/ruta>"""
import sys
from urllib.error import HTTPError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser

UA = "Mozilla/5.0 (compatible; PortfolioDemoBot/1.0)"


def main(url: str) -> None:
    parts = urlparse(url)
    robots_url = urljoin(f"{parts.scheme}://{parts.netloc}", "/robots.txt")
    rp = RobotFileParser()
    try:
        content = urlopen(Request(robots_url, headers={"User-Agent": UA}), timeout=15).read().decode("utf-8", "ignore")
        rp.parse(content.splitlines())
        print(f"robots.txt encontrado en {robots_url}:\n" + "\n".join(content.splitlines()[:25]))
        print(f"\n¿Permite a nuestro bot abrir {url}? ->", "SÍ" if rp.can_fetch(UA, url) else "NO")
    except HTTPError as exc:
        if exc.code == 404:
            print(f"No existe robots.txt ({robots_url}): no hay restricciones declaradas ahí.")
            print("Aun así revisa los términos de uso del sitio antes de extraer datos.")
        else:
            print(f"Error HTTP {exc.code} leyendo robots.txt. Revisa manualmente.")
    except Exception as exc:  # noqa: BLE001
        print(f"No se pudo leer robots.txt ({exc}). Esto NO equivale a permiso: revisa los términos del sitio.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Uso: python scripts/check_robots.py <url>")
    main(sys.argv[1])