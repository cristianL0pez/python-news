import csv
csv.field_size_limit(131072 * 10)  
def count_posts_in_csv(csv_file_path):
    try:
        with open(csv_file_path, mode="r", encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file)
            # Excluimos la primera fila que suele ser la cabecera
            header = next(reader, None)
            return sum(1 for row in reader)
    except FileNotFoundError:
        return 0

# Uso del código para obtener el número de posts
csv_file_path = "posts_data.csv"
number_of_posts = count_posts_in_csv(csv_file_path)
print(f"Número de posts en el CSV: {number_of_posts}")