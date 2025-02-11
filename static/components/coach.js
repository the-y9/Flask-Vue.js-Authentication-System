export default {
    template:`  <div>
                    <section class="poster">
                        <div class="poster-content">
                            <h1 class="poster-tile">Hi, {{ username }}</h1>
                            <p class="poster-subtitle">Sort and manage your club.</p>
                        </div>
                    </section>

                    <section class="">
                        <!-- Check if health data is available -->
                        <div v-if="healthData && healthData.data.length">
                            <ul>
                                <!-- Loop through the health data and display each record -->
                                <li v-for="record in healthData.data" :key="record.id">
                                <strong>Record ID:</strong> {{ record.id }}<br>
                                <strong>User ID:</strong> {{ record.user_id }}<br>
                                <strong>Coach ID:</strong> {{ record.coach_id }}<br>
                                <strong>Recorded At:</strong> {{ record.recorded_at }}<br>
                                <strong>Health Data:</strong>
                            <ul>
                                    <li><strong>BMI:</strong> {{ record.health_data.bmi }}</li>
                                    <li><strong>Body Fat Percentage:</strong> {{ record.health_data.body_fat_percentage }}</li>
                                    <li><strong>Calories Burned:</strong> {{ record.health_data.calories_burned }}</li>
                                    <li><strong>Steps:</strong> {{ record.health_data.steps }}</li>
                                    <li><strong>Weight:</strong> {{ record.health_data.weight }}</li>
                            </ul>
                                </li>
                            </ul>
                        </div>
                        <!-- If no data is available -->
                        <div v-else>
                            <p>No health data available.</p>
                        </div>
                    </section>
                </div>
            `,
  data() {
    return {
        username: localStorage.getItem('username'),
        healthData: [],
    };
  },

  async beforeCreate() {
    try {
        const id = 2;
        const response = await fetch(`/health-tracker/${id}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Failed to fetch data.');
        }

        this.healthData = data;
    } catch (error) {
        console.error('Error fetching data:', error);
        alert('Failed to load projects. Please try again later.');
    }

  },

};

