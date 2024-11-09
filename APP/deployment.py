import subprocess
import sys

# result = subprocess.run('minikube', 'image', 'load', 'django-app:latest', capture_output=True, text=True)
# result = subprocess.run('minikube', 'image', 'load', 'nginx:latest', capture_output=True, text=True)


files = ['static-pvc.yml',
        'media-pvc.yml',
         'postgres-pvc',
        'postgres-deployment.yml',
         'postgres-service.yml',
         'redis-deployment.yml',
         'redis-service.yml',
         'django-deployment.yml',
         'django-service.yml',
         'nginx-configmap.yml',
         'nginx-deployment.yml',
         'nginx-service.yml',
         ]

for file in files:

    command = ['kubectl', 'apply', '-f', file]

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"Deployed: {file}")
    else:
        print(f"Error: {file}")
        print(result.stderr)


