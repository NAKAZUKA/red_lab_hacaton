import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest
import numpy as np

def safe_divide(x, y):
    if y == 0:
        return np.nan
    else:
        return x / y

def generate_and_save_plots(file_path, result_folder):
    print('start')
    data = pd.read_csv(file_path, sep='\t', low_memory=False)


    web_response_data = data[(data.iloc[:, 10] == 'java') & (data.iloc[:, 11] == '[GMonit] Collector') & (data.iloc[:, 1] == 'HttpDispatcher')]
    throughput_data = data[(data.iloc[:, 10] == 'java') & (data.iloc[:, 11] == '[GMonit] Collector') & (data.iloc[:, 1] == 'HttpDispatcher')]
    apdex_data = data[(data.iloc[:, 10] == 'java') & (data.iloc[:, 11] == '[GMonit] Collector') & (data.iloc[:, 1] == 'Apdex')]
    error_data = data[(data.iloc[:, 10] == 'java') & (data.iloc[:, 11] == '[GMonit] Collector') & (data.iloc[:, 1].isin(['HttpDispatcher', 'Errors/allWeb']))]

    web_response_data_grouped = web_response_data.groupby(web_response_data.iloc[:, 2]).apply(lambda x: x.iloc[:, 4].sum() / x.iloc[:, 3].sum()).iloc[-200:]
    throughput_data_grouped = throughput_data.groupby(throughput_data.columns[2]).apply(lambda x: x.iloc[:, 3].sum()).iloc[-200:]
    apdex_data_grouped = apdex_data.groupby(apdex_data.columns[2], group_keys=False).apply(lambda x: (x.iloc[:, 3].sum() + x.iloc[:, 4].sum() / 2) / (x.iloc[:, 3].sum() + x.iloc[:, 4].sum() + x.iloc[:, 5].sum())).iloc[-200:]
    error_data_grouped = error_data.groupby(by=error_data.columns[2]).apply(
        lambda x: safe_divide(
            x[x.iloc[:, 1] == 'Errors/allWeb'].iloc[:, 3].sum(),
            x[x.iloc[:, 1] == 'HttpDispatcher'].iloc[:, 3].sum()
        )
    ).iloc[-200:]
    clf = IsolationForest(contamination=0.05)

    web_response_predictions = clf.fit_predict(web_response_data_grouped.values.reshape(-1, 1))
    throughput_predictions = clf.fit_predict(throughput_data_grouped.values.reshape(-1, 1))
    apdex_predictions = clf.fit_predict(apdex_data_grouped.values.reshape(-1, 1))
    error_predictions = clf.fit_predict(error_data_grouped.values.reshape(-1, 1))
    plt.figure()
    plt.plot(throughput_data_grouped.index, throughput_data_grouped.values, label='Throughput Data')
    plt.scatter(throughput_data_grouped.index[web_response_predictions == -1], throughput_data_grouped.values[web_response_predictions == -1], color='red', marker='s', label='Anomaly')
    plt.xlabel('Время')
    plt.ylabel('Значение')
    plt.legend()
    plt.title('Пропускная способность сервиса за время')
    plt.savefig(os.path.join(result_folder, 'throughput.png'))
    plt.close()

    plt.figure()
    plt.plot(apdex_data_grouped.index, apdex_data_grouped.values, label='Apdex Data')
    plt.scatter(apdex_data_grouped.index[web_response_predictions == -1], apdex_data_grouped.values[web_response_predictions == -1], color='red', marker='s', label='Anomaly')
    plt.xlabel('Время')
    plt.ylabel('Значение')
    plt.legend()
    plt.title('Сводный синтетический показатель “здоровья” сервиса за время')
    plt.savefig(os.path.join(result_folder, 'apdex.png'))
    plt.close()

    plt.figure()
    plt.plot(web_response_data_grouped.index, web_response_data_grouped.values, label='Web Response Data')
    plt.scatter(web_response_data_grouped.index[web_response_predictions == -1], web_response_data_grouped.values[web_response_predictions == -1], color='red', marker='s', label='Anomaly')
    plt.xlabel('Время')
    plt.ylabel('Значение')
    plt.legend()
    plt.title('Время ответа сервиса на внешний http-запрос.')
    plt.savefig(os.path.join(result_folder, 'web_response.png'))
    plt.close()

    plt.figure()
    plt.plot(error_data_grouped.index, error_data_grouped.values, label='Error Data')
    plt.scatter(error_data_grouped.index[web_response_predictions == -1], error_data_grouped.values[web_response_predictions == -1], color='red', marker='s', label='Anomaly')
    plt.xlabel('Время')
    plt.ylabel('Значение')
    plt.legend()
    plt.title('Процент ошибок в обработанных запросах за время')
    plt.savefig(os.path.join(result_folder, 'errors.png'))
    plt.close()

    correlation_matrix = pd.concat([web_response_data_grouped, throughput_data_grouped, apdex_data_grouped, error_data_grouped], axis=1).corr()

    # Вывод всех пар столбцов с их корреляцией
    for col1 in correlation_matrix.columns:
        for col2 in correlation_matrix.columns:
            if col1 != col2:
                correlation = correlation_matrix.loc[col1, col2]
                if correlation >= 0.5:
                    a = f'Значение {col1} и {col2} имеют зависимость друг с другом'
                    print(f"Значение {col1} и {col2} имеют зависимость друг с другом")
                elif correlation <= -0.5:
                    b = f'Значение {col1} и {col2} имеют зависимость друг с другом'
                    print(f"Значение {col1} и {col2} имеют зависимость друг с другом")
    most_dependent_metric = correlation_matrix.idxmax().idxmax()
    print(f"Самое значимая метрика: {most_dependent_metric}")
    plt.figure()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
    plt.title('Корреляция метрик')
    plt.savefig(os.path.join(result_folder, 'correlation_matrix.png'))
    plt.close()
