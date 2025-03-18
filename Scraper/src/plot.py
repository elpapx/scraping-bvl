import pandas as pd
import matplotlib.pyplot as plt

# Cargar los datos
data = pd.read_csv('data/bvl_data.csv')

# Verificar datos
print(data.head())

# Crear el gráfico
plt.figure(figsize=(10, 6))
for company in data['companyName'].unique():
    company_data = data[data['companyName'] == company]
    plt.plot(pd.to_datetime(company_data['timestamp']), company_data['buy'], label=company)

# Añadir leyenda y etiquetas
plt.legend()
plt.xlabel('Timestamp')
plt.ylabel('Buy Price')
plt.title('BVL Stock Data')
plt.xticks(rotation=45)
plt.tight_layout()

# Mostrar el gráfico
plt.show()