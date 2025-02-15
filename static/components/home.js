export default {
  template: `
    <div class="landing-page">
    
      <!-- poster Section -->
      <section class="poster">
        <div class="poster-content">
          <h1 class="poster-title">Seek</h1>
          <p class="poster-subtitle">Sort and manage your club.</p>
          <button class="btn btn-1" @click="goToRegister">Get Started</button>
        </div>
      </section>

      <!-- Features Section -->
      <section class="features">
        <h2 class="section-title">Why Choose Our Authentication System?</h2>
        <center>
        <div class="feature-cards">
          <div class="feature-card" v-for="feature in features" :key="feature.id">
            <img :src="feature.image" alt="Feature Image" class="feature-image" />
            <h3 class="feature-title">{{ feature.title }}</h3>
            <p class="feature-description">{{ feature.description }}</p>
          </div>
        </div>
        </center>
      </section>

      <!-- Call-to-Action Section -->
      <section class="cta-section">
        <h2 class="cta-title">Ready to Build Your Account?</h2>
        <p class="cta-subtitle">Sign up today to manage your login credentials and access secure features.</p>
        <button class="cta-button" @click="goToRegister">Sign Up Now</button>
      </section>

    </div>
  `,
  data() {
    return {
      userRole: localStorage.getItem('role'),
      features: [
        { 
          id: 1, 
          title: "Secure Login", 
          description: "Provides a secure login system using hashed passwords for user authentication.", 
          image: "static/images/hash.png" 
        },
        { 
          id: 2, 
          title: "Role-Based Authorization", 
          description: "Easily manage different user roles and control access based on user privileges.", 
          image: "static/images/role.png" 
        },
        { 
          id: 3, 
          title: "Easy User Registration", 
          description: "Simple sign-up process to create a new account and start using the system immediately.", 
          image: "static/images/signup.jpg" 
        }
      ]
    }
  },
  
  methods: {
    goToRegister() {
      this.$router.push('/register');
    }
  }
}
