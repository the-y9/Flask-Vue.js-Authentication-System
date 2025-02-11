export default {
  template: `
 <div>
    <div>
    <nav class="navbar">
      <a href="/" class="navbar-brand" >Seek</a>
      <div class="nav-links">
        <a class="nav-link" v-if="role">Role - {{ role }}</a>
        
        <router-link v-if="!is_login" class="nav-link" to="/login">Login</router-link>
        <router-link v-if="!is_login" class="nav-link" to="/register">Register</router-link>
        <button v-if="is_login" class="nav-link" @click="logout">Logout</button>
      </div>
    </nav>
    </div>
  </div>
    `,

  data() {
    return {
      role: localStorage.getItem('role'),
      is_login: !!localStorage.getItem('auth-token'), // Ensure boolean
      username: '',
    };
  },

  methods: {
    
    clearAllLocalStorage() {
      Object.keys(localStorage).forEach(key => {
        localStorage.removeItem(key);
      });
    },
    
    logout() {
      this.clearAllLocalStorage();
      this.$router.push({ path: '/login' });
    },

  },
};
