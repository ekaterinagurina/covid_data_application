<template>
  <div>
    <h1>Welcome to the COVID Dashboard</h1>
    <p>Data visualization and tracking</p>

    <div v-if="!user">
      <p>
        Please
        <router-link to="/login">log in</router-link>
        or
        <router-link to="/register">register</router-link>
        to access data.
      </p>
    </div>

    <div v-else>
      <p>Logged in as: {{ user.username }} ({{ user.email }})</p>
      <button @click="logout">Logout</button>

      <h2>COVID Data</h2>

      <div>
        <select v-model="selectedTable">
          <option disabled value="">Select a table</option>
          <option v-for="table in tables" :key="table" :value="table">
            {{ table }}
          </option>
        </select>

        <select v-model="selectedColumn">
          <option disabled value="">Select a column</option>
          <option v-for="column in plotColumns" :key="column" :value="column">
            {{ column }}
          </option>
        </select>

        <input type="text" v-model="selectedCountry" placeholder="Enter country" />

        <button @click="fetchTableData">Load Data</button>
        <button @click="fetchChart" :disabled="!selectedTable || !selectedColumn">
          Plot Chart
        </button>
      </div>

      <div v-if="chartUrl">
        <h3>Chart for {{ selectedColumn }}</h3>
        <img :src="chartUrl" alt="Chart Image" />
      </div>

      <table v-if="data.length">
        <thead>
          <tr>
            <th v-for="(value, key) in data[0]" :key="key">
              {{ key }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, index) in data" :key="index">
            <td v-for="(value, key) in row" :key="key">
              {{ value }}
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else>No data available</p>

      <h2>Statistics</h2>
      <input
        type="text"
        v-model="statCountry"
        placeholder="Country for Case Fatality Rate (CFR)"
      />
      <button @click="fetchCFR">Count Case Fatality Rate</button>
      <div v-if="cfrResult">
        <p>
          CFR for
          {{ cfrResult.country || "all countries" }}:
          <strong
            >{{ cfrResult.cfr !== null
              ? cfrResult.cfr.toFixed(2) + "%"
              : "N/A" }}</strong
          >
        </p>
        <p>
          Total cases: {{ cfrResult.total_cases }},
          Total deaths: {{ cfrResult.total_deaths }}
        </p>
      </div>

      <h2>Cases by Year and Type</h2>
      <div>
        <input v-model="compareYear" placeholder="Year (e.g. 2021)" />
        <input v-model="compareCountry" placeholder="Country (optional)" />
      </div>
      <div>
        <label><input type="checkbox" value="confirmed" v-model="selectedTypes" /> Confirmed</label>
        <label><input type="checkbox" value="death" v-model="selectedTypes" /> Deaths</label>
        <label><input type="checkbox" value="recovery" v-model="selectedTypes" /> Recovered</label>
      </div>
      <button @click="openCompareChart">Open Chart</button>

      <h2>Interactive GeoMap</h2>
      <div style="margin-top: 20px;">
        <iframe
            src="http://localhost:3000/d-solo/c6fc91ae-2486-484a-92a6-bd10c2bf13c3/new-dashboard?orgId=1&timezone=browser&tab=transformations&panelId=1&__feature.dashboardSceneSolo"
            width="1200"
            height="800"
            frameborder="0">
        </iframe>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      user: null,
      tables: [
        "coronavirus_daily",
        "coronavirus_2020",
        "coronavirus_2021",
        "coronavirus_2022",
        "coronavirus_2023",
        "covid19_vaccine",
        "world_population",
      ],
      plotColumns: ["cases", "people_at_least_one_dose"],
      selectedTable: "",
      selectedColumn: "cases",
      selectedCountry: "",
      data: [],
      chartUrl: null,
      statCountry: "",
      cfrResult: null,
      compareYear: "",
      compareCountry: "",
      selectedTypes: ["confirmed", "death", "recovery"]
    };
  },
  async created() {
    const token = localStorage.getItem("token");
    if (token) {
      try {
        const response = await axios.get("/users/me", {
          headers: { Authorization: `Bearer ${token}` },
        });
        this.user = response.data;
      } catch (error) {
        console.error("Failed to fetch user data", error);
        localStorage.removeItem("token");
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
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        });
        this.data = response.data;
        if (!this.data.length) {
          alert("No data found for the selected country or table.");
        }
      } catch (error) {
        console.error("Error fetching data:", error);
        alert("An error occurred while fetching data.");
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
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          responseType: "blob",
        });
        this.chartUrl = URL.createObjectURL(response.data);
      } catch (error) {
        console.error("Error fetching chart:", error);
        this.chartUrl = null;
      }
    },
    async fetchCFR() {
      let url = `/stats/cfr`;
      if (this.statCountry) {
        url += `?country=${encodeURIComponent(this.statCountry)}`;
      }
      try {
        const res = await axios.get(url, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        });
        this.cfrResult = res.data;
      } catch (err) {
        console.error("Could not fetch CFR:", err);
        alert("Could not fetch Case Fatality Rate.");
        this.cfrResult = null;
      }
    },
    openCompareChart() {
      if (!this.compareYear || !this.selectedTypes.length) {
        alert("Please select year and case types.");
        return;
      }

      const params = new URLSearchParams();
      if (this.compareCountry) params.append("country", this.compareCountry);
      this.selectedTypes.forEach(t => params.append("type", t));

      const url = `${window.location.origin.replace(":8080", ":8000")}/plotly/compare_types/${this.compareYear}?` + params.toString();
      window.open(url, "_blank");
    },
    logout() {
      localStorage.removeItem("token");
      this.user = null;
      this.$router.push("/login");
    },
  },
};
</script>

<style>
table {
  width: 100%;
  border-collapse: collapse;
}
th,
td {
  border: 1px solid black;
  padding: 8px;
  text-align: left;
}
img {
  max-width: 100%;
  height: auto;
  margin-top: 20px;
}
h2 {
  margin-top: 30px;
}
</style>
