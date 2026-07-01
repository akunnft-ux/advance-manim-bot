from templates.base import BaseTemplate
from templates.kalkulus import DerivativeScene, IntegralScene
from templates.aljabar import VectorScene, TransformScene
from templates.geometri import SphereScene, CrossSectionScene
from templates.probstat import DistribusiScene, BayesScene

TEMPLATE_REGISTRY = {
    "derivative": DerivativeScene,
    "integral": IntegralScene,
    "vector": VectorScene,
    "transform": TransformScene,
    "sphere": SphereScene,
    "cross_section": CrossSectionScene,
    "distribusi": DistribusiScene,
    "bayes": BayesScene,
}

TEMPLATE_TOPIC_MAP = {
    "kalkulus": ["derivative", "integral"],
    "aljabar-linear": ["vector", "transform"],
    "geometri-3d": ["sphere", "cross_section"],
    "probstat": ["distribusi", "bayes"],
}
