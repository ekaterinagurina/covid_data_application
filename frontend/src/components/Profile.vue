<template>
  <div>
    <h2>User Profile</h2>
    <p v-if="user">Welcome, {{ user.username }} ({{ user.email }})</p>
    <button @click="logout">Logout</button>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      user: null,
      errorMessage: ''
    };
  },
  async created() {
    const token = localStorage.getItem('token');
    if (!token) {
      this.$router.push('/login');
      return;
    }

    try {
      const response = await axios.get('/users/me', {
        headers: { Authorization: `Bearer ${token}` }
      });
      this.user = response.data;
    } catch (error) {
      this.errorMessage = 'Failed to fetch user data';
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('token');
      this.$router.push('/login');
    }
  }
};
</script>

<style>
.error {
  color: red;
}
</style>
