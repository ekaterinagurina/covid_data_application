<template>
  <div>
    <h1>COVID Data</h1>

    <!-- Dropdown to select the table -->
    <select v-model="selectedTable" @change="fetchTableData">
      <option disabled value="">Please select a table</option>
      <option v-for="table in tables" :key="table" :value="table">{{ table }}</option>
    </select>

    <!-- Input for selecting the country -->
    <input type="text" v-model="selectedCountry" placeholder="Enter country name" />

    <!-- Button to fetch data based on selected country -->
    <button @click="fetchTableData">Fetch Data</button>

    <!-- Show the table only if data is available -->
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
      tables: [  // List of available tables
        "country_wise_latest",
        "covid_19_clean_complete",
        "day_wise",
        "full_grouped",
        "usa_county_wise",
        "worldometer_data"
      ],
      selectedTable: "",  // Store the selected table here
      selectedCountry: "",  // Store the selected country here
      data: []  // The fetched data will go here
    };
  },
  methods: {
    fetchTableData() {
      if (this.selectedTable) {
        // Build the URL with the country filter if selected
        let url = `http://localhost:8000/data/${this.selectedTable}`;
        if (this.selectedCountry) {
          url += `?country=${encodeURIComponent(this.selectedCountry)}`;
        }

        // Fetch the data from the selected table and country
        axios.get(url)
          .then(response => {
            console.log("Data fetched:", response.data);
            this.data = response.data;
          })
          .catch(error => {
            console.error("Error fetching data:", error);
          });
      } else {
        this.data = [];
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
</style>
