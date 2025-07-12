
import streamlit as st
import math
import pandas as pd
import matplotlib.pyplot as plt
import io

st.title("Heat Balance Test Calculator")
st.subheader("Four Stroke Diesel Engine with Electrical Loading")

st.markdown("""
This application calculates heat balance for a four-stroke diesel engine with electrical loading.
Enter your test readings below to generate the heat balance data sheet and visualization.
""")

# Constants
Cv = 42886  # kj/kg
Density = 832  # kg/s
C_Water = 4.186  # kj/kg
A_orifice = (math.pi/4) * (2.54*10**-2)**2  # m2
D_orifice = 2.54*10**-2  # m
Density_water = 1000  # kg/m
V = 220  # Volt
Speed = 1500  # rpm
FC_volume = 25*10**-6  # m3
Atm_P = 1.013*10**5  # Pa
R = 287  # J/kg
C_gas = 1.005  # kj/kg

# Display constants
with st.expander("View Engine Constants"):
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Calorific Value (Cv):** {Cv} kJ/kg")
        st.write(f"**Fuel Density:** {Density} kg/m³")
        st.write(f"**Water Specific Heat:** {C_Water} kJ/kg·K")
        st.write(f"**Orifice Area:** {A_orifice:.6f} m²")
        st.write(f"**Orifice Diameter:** {D_orifice} m")
    with col2:
        st.write(f"**Water Density:** {Density_water} kg/m³")
        st.write(f"**Voltage:** {V} V")
        st.write(f"**Engine Speed:** {Speed} rpm")
        st.write(f"**Fuel Consumption Volume:** {FC_volume*1e6} cm³")
        st.write(f"**Atmospheric Pressure:** {Atm_P} Pa")

# Input section
st.header("Test Readings Input")

n = st.number_input("Number of Readings:", min_value=1, max_value=10, value=1, step=1)

Input_list = []
for i in range(int(n)):
    st.subheader(f"Reading {i+1}")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        Load = st.number_input(f"Load (Amp) - Reading {i+1}:", value=0, key=f"load_{i}")
        TT_FC = st.number_input(f"Time for 25cc fuel consumption (s) - Reading {i+1}:", value=0.0, key=f"tt_fc_{i}")
        In_Water_Temp = st.number_input(f"Input Water Temperature (°C) - Reading {i+1}:", value=0, key=f"in_water_{i}")
        Out_water_temp = st.number_input(f"Output Water Temperature (°C) - Reading {i+1}:", value=0, key=f"out_water_{i}")
    
    with col2:
        m_water = st.number_input(f"Water collection in 30s (kg) - Reading {i+1}:", value=0.0, key=f"m_water_{i}")
        In_gas_Temp = st.number_input(f"Input Gas Temperature (°C) - Reading {i+1}:", value=0, key=f"in_gas_{i}")
        Out_gas_Temp = st.number_input(f"Output Gas Temperature (°C) - Reading {i+1}:", value=0, key=f"out_gas_{i}")
    
    with col3:
        Mano_Readi_high = st.number_input(f"Manometer Reading High (cm) - Reading {i+1}:", value=0.0, key=f"mano_high_{i}")
        Mano_Readi_low = st.number_input(f"Manometer Reading Low (cm) - Reading {i+1}:", value=0.0, key=f"mano_low_{i}")
    
    # Calculate derived values
    Rise_water_temp = Out_water_temp - In_Water_Temp
    Rise_gas_temp = Out_gas_Temp - In_gas_Temp
    Mano_Reading = Mano_Readi_high - Mano_Readi_low
    
    # Append to input list
    reading_data = [
        i+1, Load, V, Speed, TT_FC, In_Water_Temp, Out_water_temp, Rise_water_temp,
        m_water, In_gas_Temp, Out_gas_Temp, Rise_gas_temp, Mano_Readi_high,
        Mano_Readi_low, Mano_Reading, D_orifice
    ]
    Input_list.append(reading_data)

if st.button("Calculate Heat Balance", type="primary"):
    if all(reading[4] > 0 for reading in Input_list):  # Check if TT_FC > 0 for all readings
        # Display input data
        st.header("Input Data Summary")
        Column_names = ["S.No", "I (Amp)", "V(Volts)", "Speed(RPM)", "Time for 25cc fuel (s)",
                       "Input Water Temp (°C)", "Output Water Temp (°C)", "Rise in Water Temp (°C)",
                       "Water collection in 30s (kg)", "Input Gas Temp (°C)", "Output Gas Temp (°C)",
                       "Rise in Gas Temp (°C)", "h1(cm)", "h2(cm)", "Difference (h1-h2)", "Orifice Diameter (m)"]
        
        df = pd.DataFrame(Input_list, columns=Column_names)
        st.dataframe(df)
        
        # Calculations
        Output_list = []
        for i in range(int(n)):
            Mass_flow_fuel = (FC_volume/Input_list[i][4])
            Qin = (FC_volume/Input_list[i][4]) * Density * 3600 * Cv  # KJ/hr
            Density_air = (Atm_P) / (R * (273 + Input_list[i][9]))
            Vol_flow_rate = math.sqrt((2 * 9.81 * 1000 * (Input_list[i][14] * 10**-2)) / Density_air) * A_orifice  # m3/s
            Mass_flow_rate = Vol_flow_rate * Density_air * 3600  # kg/hr
            Qex = (Mass_flow_rate + Mass_flow_fuel * 3600) * C_gas * Input_list[i][11]  # KJ/hr
            Qex_per = (Qex * 100) / Qin
            BP_W = V * Input_list[i][1] * (10**-3)
            BP = V * Input_list[i][1] * 3600 * (10**-3)  # KJ/hr
            BP_per = (BP * 100) / Qin
            Qcw = ((Input_list[i][8] / 30) * 3600 * C_Water * Input_list[i][7])  # KJ/hr
            Qcw_per = (Qcw * 100) / Qin
            Unacc_loss = Qin - Qex - BP - Qcw
            Unacc_loss_per = (Unacc_loss * 100) / Qin
            
            output_data = [
                i+1, round(BP_W, 2), round(Qin, 2), round(BP, 2), round(BP_per, 2),
                round(BP_per, 2), round(Qcw, 2), round(Qcw_per, 2), Qcw_per + BP_per,
                round(Qex, 2), round(Qex_per, 2), Qex_per + Qcw_per + BP_per,
                round(Unacc_loss, 2), round(Unacc_loss_per, 2), Unacc_loss_per + Qex_per + Qcw_per + BP_per
            ]
            Output_list.append(output_data)
        
        # Display results
        st.header("Heat Balance Data Sheet (Hourly Basis)")
        Column_names_2 = ["S.No", "BP (W)", "Qin (KJ/hr)", "BP (KJ/hr)", "BP (%)", "BP (Cumulative %)",
                         "Qcw (KJ/hr)", "Qcw (%)", "Qcw (Cumulative %)", "Qex (KJ/hr)", "Qex (%)",
                         "Qex (Cumulative %)", "Unacc. Loss (KJ/hr)", "Unacc. Loss (%)", "Unacc. Loss (Cumulative %)"]
        
        df_2 = pd.DataFrame(Output_list, columns=Column_names_2)
        st.dataframe(df_2)
        
        # Download buttons
        col1, col2 = st.columns(2)
        with col1:
            csv1 = df.to_csv(index=False)
            st.download_button(
                label="Download Input Data CSV",
                data=csv1,
                file_name='Heat_Balance_Input_Data.csv',
                mime='text/csv'
            )
        
        with col2:
            csv2 = df_2.to_csv(index=False)
            st.download_button(
                label="Download Results CSV",
                data=csv2,
                file_name='Heat_Balance_Results.csv',
                mime='text/csv'
            )
        
        # Plotting
        st.header("Heat Balance Graph")
        
        x = [row[1] for row in Output_list]  # BP (W)
        y1 = [row[5] for row in Output_list]  # BP (Cumulative %)
        y2 = [row[8] for row in Output_list]  # Qcw (Cumulative %)
        y3 = [row[11] for row in Output_list]  # Qex (Cumulative %)
        y4 = [row[14] for row in Output_list]  # Unacc. Loss (Cumulative %)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(x, y1, label='BP (Cumulative %)', marker='o')
        ax.plot(x, y2, label='Qcw (Cumulative %)', marker='s')
        ax.plot(x, y3, label='Qex (Cumulative %)', marker='^')
        ax.plot(x, y4, label='Unacc. Loss (Cumulative %)', marker='d')
        
        ax.set_title('Heat Balance Graph')
        ax.set_xlabel('BP (kW)')
        ax.set_ylabel('Percentage')
        ax.legend()
        ax.grid(True)
        
        st.pyplot(fig)
        
        # Download plot
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        st.download_button(
            label="Download Graph (PNG)",
            data=img_buffer,
            file_name='heat_balance_graph.png',
            mime='image/png'
        )
    
    else:
        st.error("Please ensure all 'Time for 25cc fuel consumption' values are greater than 0.")

st.markdown("---")
st.markdown("*This code was originally written by RAGUBALA M on 12/07/2025*")
st.markdown("*Converted to web application for public use*")
