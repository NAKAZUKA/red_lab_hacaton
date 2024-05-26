import pandas as pd

def reduce_tsv(file_path, output_path, num_rows):
    # Чтение указанного количества строк из исходного файла TSV
    data = pd.read_csv(file_path, sep='\t', nrows=num_rows)
    
    # Сохранение этих строк в новый файл TSV
    data.to_csv(output_path, sep='\t', index=False)

# Путь к исходному файлу TSV
input_file_path = 'metrics_collector.tsv'

# Путь к выходному файлу TSV
output_file_path = 'metrics_collector.tsv2'

# Количество строк, которые нужно сохранить
number_of_rows = 5000000

# Вызов функции для сокращения файла
reduce_tsv(input_file_path, output_file_path, number_of_rows)
