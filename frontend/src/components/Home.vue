<template>
  <div>
    <h1>Welcome to the COVID Dashboard</h1>
    <p>Data visualization and tracking</p>

    <div v-if="!user">
      <p>Please <router-link to="/login">log in</router-link> or <router-link to="/register">register</router-link> to access data.</p>
    </div>

    <div v-if="user">
      <p>Logged in as: {{ user.username }} ({{ user.email }})</p>
      <button @click="logout">Logout</button>

      <!-- Fetch and display COVID data -->
      <h2>COVID Data</h2>
      <select v-model="selectedTable" @change="fetchTableData">
        <option disabled value="">Select a table</option>
        <option v-for="table in tables" :key="table" :value="table">{{ table }}</option>
      </select>

      <input type="text" v-model="selectedCountry" placeholder="Enter country name" />
      <button @click="fetchTableData">Fetch Data</button>

      <select v-model="selectedColumn" :disabled="!selectedTable">
        <option disabled value="">Select a column to plot</option>
        <option v-for="column in plotColumns" :key="column" :value="column">{{ column }}</option>
      </select>

      <button @click="fetchChart" :disabled="!selectedColumn || !selectedTable">Plot Chart</button>

      <div v-if="chartUrl">
        <h3>Chart for {{ selectedColumn }}</h3>
        <img :src="chartUrl" alt="Chart Image" />
      </div>

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
      <p v-else>No data available</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      user: null,
      tables: [
        "country_wise_latest",
        "covid_19_clean_complete",
        "day_wise",
        "full_grouped",
        "usa_county_wise",
        "worldometer_data"
      ],
      plotColumns: ["confirmed", "deaths", "recovered", "active"],
      selectedTable: "",
      selectedCountry: "",
      selectedColumn: "",
      data: [],
      chartUrl: null
    };
  },
  async created() {
    // Get user data if logged in
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const response = await axios.get('/users/me', {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.user = response.data;
      } catch (error) {
        console.error("Failed to fetch user data", error);
        localStorage.removeItem('token');
      }
    }
  },
  methods: {
    async fetchTableData() {
      if (!this.selectedTable) return;

      let url = `/data/${this.selectedTable}`;
      if (this.selectedCountry) {
        url += `?country=${encodeURIComponent(this.selectedCountry)}`;
      }

      try {
        const response = await axios.get(url, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        this.data = response.data;
      } catch (error) {
        console.error("Error fetching data:", error);
        this.data = [];
      }
    },
    async fetchChart() {
      if (!this.selectedTable || !this.selectedColumn) return;

      let url = `/plot/${this.selectedTable}/${this.selectedColumn}`;
      if (this.selectedCountry) {
        url += `?country=${encodeURIComponent(this.selectedCountry)}`;
      }

      try {
        const response = await axios.get(url, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
          responseType: 'blob'
        });
        const urlCreator = window.URL || window.webkitURL;
        this.chartUrl = urlCreator.createObjectURL(response.data);
      } catch (error) {
        console.error("Error fetching chart:", error);
        this.chartUrl = null;
      }
    },
    logout() {
      localStorage.removeItem('token');
      this.user = null;
      this.$router.push('/login');
    }
  }
};
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
