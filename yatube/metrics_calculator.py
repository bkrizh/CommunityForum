import django.apps
from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt
import os
import django
from django.db import models

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yatube.settings')
django.setup()

def calculate_metrics():
    metrics = defaultdict(dict)

    # Получаем все модели из всех зарегистрированных приложений Django
    for app_config in django.apps.apps.get_app_configs():
        for model in app_config.get_models():
            outgoing_relations = model._meta.related_objects
            incoming_relations = model._meta.get_fields()

            if len(outgoing_relations) + len(incoming_relations) == 0:
                instability = 0
            else:
                instability = len(outgoing_relations) / (len(outgoing_relations) + len(incoming_relations))

            abstract_fields = [field for field in model._meta.fields if isinstance(field, models.AutoField)]
            if len(model._meta.fields) == 0:
                abstractness = 0
            else:
                abstractness = len(abstract_fields) / len(model._meta.fields)

            metrics[model.__name__] = {'Instability': instability, 'Abstractness': abstractness}

    return metrics


def plot_metrics(metrics):
    df = pd.DataFrame(metrics).T
    print(df)
    df.plot(kind='bar')
    plt.show()


if __name__ == "__main__":
    metrics = calculate_metrics()
    plot_metrics(metrics)
