# Kubernetes Setup for url-shortner (Minikube)

This deploys your Dockerized Flask app (`antonpas210/url-shortner:v1`) locally with:
- Deployment (+ReplicaSet/Pods)
- Service (NodePort)
- HPA (CPU-based)
- ConfigMap & Secret
- CronJob
- Liveness/Readiness probes

## 0) Prereqs
brew install kubectl minikube
minikube start --driver=docker --cpus=4 --memory=6g
minikube addons enable metrics-server

## 1) Apply manifests
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/cronjob.yaml

kubectl rollout status deploy/url-shortner
kubectl get deploy,rs,pods,svc,hpa,cronjob

## 2) Access
NodePort: http://$(minikube ip):30080/
Or port-forward: kubectl port-forward svc/web 8000:8000  # http://localhost:8000/

## 3) HPA / CronJob
kubectl top pods
kubectl get hpa url-shortner-hpa
kubectl get cronjob
kubectl get jobs --sort-by=.metadata.creationTimestamp | tail -n 1

## 4) Clean up
kubectl delete -f k8s/cronjob.yaml -f k8s/hpa.yaml -f k8s/service.yaml -f k8s/deployment.yaml -f k8s/secret.yaml -f k8s/configmap.yaml
minikube delete
