from prometheus_client import Gauge
from prometheus_client import start_http_server, multiprocess, CollectorRegistry, core
from prometheus_client import (
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from http.server import HTTPServer, BaseHTTPRequestHandler,ThreadingHTTPServer

import os
import shutil
import threading


prome_stats=os.environ.get('PROMETHEUS_MULTIPROC_DIR')
if not prome_stats:
    raise RuntimeError('Environment variable PROMETHEUS_MULTIPROC_DIR is not set. Please set it to the directory where you want to store Prometheus metrics.')

registry = CollectorRegistry()
multiprocess.MultiProcessCollector(registry)
_metrics_gauges: dict[str, Gauge] = {}
def set_metrics(metrics):
    for key, value in metrics.items():
        if not isinstance(value, (int, float)):
            print(f"Skipping non-numeric metric: {key} with value {value}")
            continue
        gauge = _metrics_gauges.get(key)
        if gauge is None:
            gauge = Gauge(
                "pg_chameleon_" + key,
                f"Metric {key}",
                multiprocess_mode="max",
                labelnames=["app"],
                registry=registry
            )
            _metrics_gauges[key] = gauge
        gauge.labels(app="pg_chameleon").set(value)

class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != '/metrics':
            return self.send_error(404)
        data = generate_latest(registry)
        self.send_response(200)
        self.send_header('Content-Type', CONTENT_TYPE_LATEST)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

def start_prometheus_server():
    if os.path.exists(prome_stats):
        shutil.rmtree(prome_stats)
    os.mkdir(prome_stats)

    server = ThreadingHTTPServer(("0.0.0.0", 8000), MetricsHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
