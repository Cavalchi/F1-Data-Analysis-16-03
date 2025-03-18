import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import fastf1
from fastf1 import plotting

def configurar_fastf1():
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams['figure.figsize'] = (15, 6)
    cache_dir = 'cache'
    os.makedirs(cache_dir, exist_ok=True)
    fastf1.Cache.enable_cache(cache_dir)
    return fastf1.get_session(2025, 'Australia', 'R')

def carregar_dados(session):
    session.load()
    pilotos = ['NOR', 'VER']
    data = {}
    for piloto in pilotos:
        laps = session.laps.pick_driver(piloto)
        data[piloto] = laps[['LapNumber', 'LapTime']].dropna()
    return data

def criar_grafico_tempos_volta(session, data):
    fig, ax1 = plt.subplots(figsize=(15, 6))  # Criar apenas um gráfico
    def format_time(x, pos):
        minutes = int(x // 60)
        seconds = x % 60
        return f'{minutes}:{seconds:05.2f}'.replace('.', ':')
    for piloto, df in data.items():
        ax1.plot(df['LapNumber'], 
                df['LapTime'].dt.total_seconds(),
                marker='o',
                linewidth=2,
                markersize=6,
                label=piloto)
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.legend()
    ax1.set_xlabel('Volta')
    ax1.set_ylabel('Tempo de Volta')
    ax1.yaxis.set_major_formatter(FuncFormatter(format_time))
    ax1.set_xlim(0, max(data['NOR']['LapNumber']) + 1)
    ax1.set_title('Tempos de Volta por Piloto')
    plt.tight_layout()
    plt.show()

def criar_grafico_posicao_corrida(session):
    fig, ax = plt.subplots(figsize=(8.0, 4.9))
    for drv in session.drivers:
        drv_laps = session.laps.pick_drivers(drv)
        abb = drv_laps['Driver'].iloc[0]
        style = fastf1.plotting.get_driver_style(identifier=abb,
                                                 style=['color', 'linestyle'],
                                                 session=session)
        ax.plot(drv_laps['LapNumber'], drv_laps['Position'],
                label=abb, **style)
    ax.set_ylim([20.5, 0.5])
    ax.set_yticks([1, 5, 10, 15, 20])
    ax.set_xlabel('Lap')
    ax.set_ylabel('Position')
    ax.legend(bbox_to_anchor=(1.0, 1.02))
    plt.tight_layout()
    plt.show()

def criar_grafico_tempos_volta_avancado(session):
    fig, ax = plt.subplots(figsize=(8, 5))
    for driver in ('NOR', 'PIA', 'VER', 'LAW'):
        laps = session.laps.pick_drivers(driver).pick_quicklaps().reset_index()
        style = plotting.get_driver_style(identifier=driver,
                                          style=['color', 'linestyle'],
                                          session=session)
        ax.plot(laps['LapTime'], **style, label=driver)
    ax.set_xlabel("Lap Number")
    ax.set_ylabel("Lap Time")
    ax.legend()
    plotting.add_sorted_driver_legend(ax, session)
    plt.show()
def criar_grafico_estategia_pneusdois(session):
    laps = session.laps
    stints = laps[['Driver', 'Stint', 'Compound', 'LapNumber']]
    stints = stints.groupby(['Driver', 'Stint', 'Compound']).count().reset_index()
    stints = stints.rename(columns={'LapNumber': 'StintLength'})
    stints['MudancaComposto'] = stints['Compound'] != stints.groupby('Driver')['Compound'].shift(1)
    stints['StintGroup'] = stints.groupby('Driver')['MudancaComposto'].cumsum()
    stints_agrupados = stints.groupby(['Driver', 'StintGroup', 'Compound']).agg({'StintLength': 'sum'}).reset_index()
    stints_agrupados = stints_agrupados.drop(['StintGroup'], axis=1)
    print("\nDados dos Stints Agrupados:")
    print(stints_agrupados.to_string(index=False))

def criar_grafico_estategia_pneus(session):
    laps = session.laps
    drivers = session.drivers
    drivers = [session.get_driver(driver)["Abbreviation"] for driver in drivers]
    stints = laps[["Driver", "Stint", "Compound", "LapNumber"]]
    stints = stints.groupby(["Driver", "Stint", "Compound"])
    stints = stints.count().reset_index()
    stints = stints.rename(columns={"LapNumber": "StintLength"})
    fig, ax = plt.subplots(figsize=(5, 10))
    for driver in drivers:
        driver_stints = stints.loc[stints["Driver"] == driver]
        previous_stint_end = 0
        for idx, row in driver_stints.iterrows():
            compound_color = plotting.get_compound_color(row["Compound"],
                                                        session=session)
            plt.barh(y=driver,
                    width=row["StintLength"],
                    left=previous_stint_end,
                    color=compound_color,
                    edgecolor="black",
                    fill=True)
            
            previous_stint_end += row["StintLength"]

    plt.title("Estratégias de Pneus")
    plt.xlabel("Número da Volta")
    plt.grid(False)
    ax.invert_yaxis()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    plt.tight_layout()
    plt.show()

def analise_corrida():
    print("Inicializando análise...")
    session = configurar_fastf1()
    data = carregar_dados(session)
    print("\n Gerando gráficos...")
    criar_grafico_tempos_volta(session, data)
    criar_grafico_posicao_corrida(session)
    criar_grafico_tempos_volta_avancado(session)
    criar_grafico_estategia_pneus(session)
    criar_grafico_estategia_pneusdois(session)
    print("\n Análise concluída!")

if __name__ == "__main__":
    analise_corrida()
