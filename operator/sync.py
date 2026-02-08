from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import json

class Controller(BaseHTTPRequestHandler):
  def sync(self, parent, children):
    # get parent specs
    spec = parent.get("spec", {})
    lambda_code = spec.get("code", "")
    replicas = spec.get("replicas", 1)
    host = spec.get("host", "localhost")

    # Compute status based on observed state.
    observed_status = {
      "configmaps": len(children["ConfigMap.v1"]),
      "services": len(children["Service.v1"]),
      "ingress": len(children["Ingress.networking.k8s.io/v1"]),
      "pods": len(children["Pod.v1"])
    }

    # Generate the desired child object(s).
    desired_children = [self.create_config_map(parent, lambda_code)]
    desired_children.append(self.create_service(parent))
    desired_children.append(self.create_ingress(parent, host))
    for i in range(replicas):
      desired_children.append(self.create_pod(parent, i))

    return {"status": observed_status, "children": desired_children}

  def create_config_map(self, parent, lambda_code):
    indented_code = map(lambda line: "    " + line, lambda_code.split('\n'))
    lambda_code = '\n'.join(indented_code)
    return {
      "apiVersion": "v1",
      "kind": "ConfigMap",
      "metadata": {
        "name": parent["metadata"]["name"]
      },
      "data": {
        "script.py": """
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urlparse
          
class Controller(BaseHTTPRequestHandler):
  def do_GET(self):
    query_params = urlparse.parse_qs(urlparse.urlparse(self.path).query)
  
    output = ""
    
    # Begin lambda
%s
    # End lambda
    
    if output == "":
      output = "Lambda output was empty"
    
    self.send_response(200)
    self.end_headers()
    self.wfile.write(output)
        
HTTPServer(("", 80), Controller).serve_forever()
        """ % lambda_code
      }
    }

  def create_pod(self, parent, i):
    return {
      "apiVersion": "v1",
      "kind": "Pod",
      "metadata": {
        "name": "%s-%s" % (parent["metadata"]["name"], i),
        "labels": {
          "app": parent["metadata"]["name"]
        }
      },
      "spec": {
        "restartPolicy": "OnFailure",
        "containers": [
          {
            "name": "hello",
            "image": "python:2.7",
            "command": ["python", "/scripts/script.py"],
            "volumeMounts": [
              {
                "name": "script",
                "mountPath": "/scripts"
              }
            ]
          }
        ],
        "volumes": [
          {
            "name": "script",
            "configMap": {
              "name": parent["metadata"]["name"]
            }
          }
        ]
      }
    }

  def create_service(self, parent):
    return {
      "apiVersion": "v1",
      "kind": "Service",
      "metadata": {
        "name": parent["metadata"]["name"]
      },
      "spec": {
        "selector": {
          "app": parent["metadata"]["name"]
        },
        "ports": [
          {
            "port": 80
          }
        ]
      }
    }

  def create_ingress(self, parent, host):
    return {
      "apiVersion": "networking.k8s.io/v1",
      "kind": "Ingress",
      "metadata": {
        "name": parent["metadata"]["name"],
        "annotations": {
          "kubernetes.io/ingress.class": "nginx",
          "kubernetes.io/tls-acme": "true",
          "cert-manager.io/cluster-issuer": "letsencrypt-staging-issuer"
        }
      },
      "spec": {
        "rules": [
          {
            "host": host,
            "http": {
              "paths": [
                {
                  "path": "/",
                  "pathType": "Prefix",
                  "backend": {
                    "service": {
                        "name": parent["metadata"]["name"],
                        "port": {
                            "number": 80
                        }
                    }
                  }
                }
              ]
            }
          },
        ],
        "tls": [
          {
            "hosts": [host],
            "secretName": "%s-%s" % (parent["metadata"]["name"], "tls-secret")
          }
        ]
      }
    }

  def do_POST(self):
    # Serve the sync() function as a JSON webhook.
    observed = json.loads(self.rfile.read(int(self.headers.getheader("content-length"))))
    desired = self.sync(observed["parent"], observed["children"])

    self.send_response(200)
    self.send_header("Content-type", "application/json")
    self.end_headers()
    self.wfile.write(json.dumps(desired))

HTTPServer(("", 80), Controller).serve_forever()