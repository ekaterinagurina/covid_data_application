<template>
  <div>
    <h1>COVID Data: Select Table, Country, and Column to Plot</h1>

    <!-- Dropdown to select the table -->
    <select v-model="selectedTable" @change="fetchTableData">
      <option disabled value="">Please select a table</option>
      <option v-for="table in tables" :key="table" :value="table">{{ table }}</option>
    </select>

    <!-- Input for selecting the country -->
    <input type="text" v-model="selectedCountry" placeholder="Enter country name" />

    <!-- Button to fetch data based on selected country -->
    <button @click="fetchTableData">Fetch Data</button>

    <!-- Dropdown to select the column for plotting -->
    <select v-model="selectedColumn" :disabled="!selectedTable" placeholder="Select column to plot">
      <option disabled value="">Select a column to plot</option>
      <option v-for="column in plotColumns" :key="column" :value="column">{{ column }}</option>
    </select>

    <!-- Button to fetch chart based on selected column -->
    <button @click="fetchChart" :disabled="!selectedColumn || !selectedTable">Plot Chart</button>

    <!-- Display the chart image if available -->
    <div v-if="chartUrl">
      <h3>Chart for {{ selectedColumn }} over Time</h3>
      <img :src="chartUrl" alt="Chart Image" />
    </div>

    <!-- Display the table data if available -->
    <table v-if="data.length">
      <thead>
        <tr>
          <th v-for="(value, key) in data[0]" :key="key">{{ key }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, index) in data" :key="index">
          <td v-for="(value, key) in row" :key="key">{{ value }}</td>
        </tr>
      </tbody>
    </table>

    <!-- Fallback if no data is available -->
    <p v-else>No data available</p>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      tables: [
        "country_wise_latest",
        "covid_19_clean_complete",
        "day_wise",
        "full_grouped",
        "usa_county_wise",
        "worldometer_data"
      ],
      plotColumns: ["confirmed", "deaths", "recovered", "active"],  // Columns available for plotting
      selectedTable: "",     // Store the selected table
      selectedCountry: "",   // Store the selected country
      selectedColumn: "",    // Store the selected column for plotting
      data: [],              // Fetched table data
      chartUrl: null         // URL for the generated chart
    };
  },
  methods: {
    fetchTableData() {
      if (this.selectedTable) {
        // Construct the URL with the country filter if selected
        let url = `http://localhost:8000/data/${this.selectedTable}`;
        if (this.selectedCountry) {
          url += `?country=${encodeURIComponent(this.selectedCountry)}`;
        }

        // Fetch the data from the backend
        axios.get(url)
          .then(response => {
            console.log("Data fetched:", response.data);
            this.data = response.data;
          })
          .catch(error => {
            console.error("Error fetching data:", error);
            this.data = [];
          });
      } else {
        this.data = [];
      }
    },
    fetchChart() {
      if (this.selectedTable && this.selectedColumn) {
        // Construct the URL for fetching the chart with optional country filter
        let url = `http://localhost:8000/plot/${this.selectedTable}/${this.selectedColumn}`;
        if (this.selectedCountry) {
          url += `?country=${encodeURIComponent(this.selectedCountry)}`;
        }

        // Fetch the chart from the backend
        axios.get(url, { responseType: 'blob' })  // Specify response type as blob for images
          .then(response => {
            // Convert the blob response to a URL
            const urlCreator = window.URL || window.webkitURL;
            this.chartUrl = urlCreator.createObjectURL(response.data);
          })
          .catch(error => {
            console.error("Error fetching chart:", error);
            this.chartUrl = null;
          });
      }
    }
  }
}
</script>

<style>
table {
  width: 100%;
  border-collapse: collapse;
}
th, td {
  border: 1px solid black;
  padding: 8px;
  text-align: left;
}
img {
  max-width: 100%;
  height: auto;
  margin-top: 20px;
}
</style>
