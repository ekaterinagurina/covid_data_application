<template>
  <div>
    <h2>Register</h2>
    <form @submit.prevent="register">
      <input v-model="username" placeholder="Username" required />
      <input v-model="email" placeholder="Email" required />
      <input v-model="password" type="password" placeholder="Password" required />
      <button type="submit">Register</button>
    </form>
    <p v-if="message" class="success">{{ message }}</p>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      username: '',
      email: '',
      password: '',
      message: '',
      errorMessage: ''
    };
  },
  methods: {
    async register() {
      try {
        await axios.post('/register', {
          username: this.username,
          email: this.email,
          password: this.password
        }, { headers: { "Content-Type": "application/json" } });

        this.message = 'User registered successfully! You can now log in.';
        this.errorMessage = '';
      } catch (error) {
        this.errorMessage = 'Registration failed. Try again.';
        this.message = '';
      }
    }
  }
};
</script>

<style>
.success { color: green; }
.error { color: red; }
</style>
