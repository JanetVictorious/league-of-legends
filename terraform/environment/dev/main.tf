provider "kubernetes" {
  config_path    = "~/.kube/config"
  config_context = "minikube"
}

provider "kubectl" {
  config_path    = "~/.kube/config"
  config_context = "minikube"
}

module "kubernetes_modules" {
  source = "../../modules/kubernetes"

  env       = var.env
  namespace = var.namespace

  providers = {
    kubernetes = kubernetes
    kubectl    = kubectl 
   }
}
