export default {
    template:`  <div>
                    <section class="poster">
                        <div class="poster-content">
                            <h1 class="poster-tile">Hi, {{ username }}</h1>
                            <p class="poster-subtitle">Sort and manage your club.</p>
                        </div>
                    </section>

                    <section class="features">
                            <div>
                                <canvas id="bmiChart"></canvas>
                            </div>
                            
                        <!-- Check if health data is available -->
                        <div v-if="healthData && healthData.data">
                            <button class='btn btn-info ' @click="toggleChartData">Toggle Data</button>
            
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Recorded At</th>
                                        <th>BMI</th>
                                        <th>Body Fat Percentage</th>
                                        <th>Calories Burned</th>
                                        <th>Steps</th>
                                        <th>Weight</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <!-- Loop through the health data and display each record -->
                                    <tr v-for="record in healthData.data" :key="record.id">
                                        <td>{{ local(record.recorded_at) }}</td>
                                        <td>{{ record.health_data.bmi }}</td>
                                        <td>{{ record.health_data.body_fat_percentage }}</td>
                                        <td>{{ record.health_data.calories_burned }}</td>
                                        <td>{{ record.health_data.steps }}</td>
                                        <td>{{ record.health_data.weight }}</td>
                                    </tr>
                                </tbody>
                            </table>

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
        showBMI: true,  // Control which data to show
        showBodyFat: false,
        showCalories: false,
        showSteps: false,
        showWeight: false,
    };
  },


  async mounted() {
    try {
        const id = 2;
        const response = await fetch(`/health-tracker/${id}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Failed to fetch data.');
        }
        this.healthData = data;
        const hdata = this.healthData.data;
        this.renderBMIChart(hdata);
    } catch (error) {
        console.error('Error fetching data:', error);
        alert('Failed to load projects. Please try again later.');
    }    
        
    },

  methods: {
    local(isoDatetimeStr) {
        // Step 1: Create a Date object from the ISO 8601 datetime string
        const date = new Date(isoDatetimeStr);
        
        // Step 2: Convert to a human-readable local time string
        const options = {
          year: 'numeric', // Example: "2025"
          month: 'long', // Example: "January"
          day: 'numeric', // Example: "16"
          hour: '2-digit', // Example: "04"
          minute: '2-digit', // Example: "18"
          second: '2-digit', // Example: "02"
        //   timeZoneName: 'short' // Example: "EST"
        };
        
        // Step 3: Format the date into a human-readable format
        const humanReadable = date.toLocaleString('en-IN', options);
        return humanReadable;
      },

      dat(datestr){
        const date = new Date(datestr);
        const options = {
            year: '2-digit',
            month: 'short',
            day: 'numeric'
        };
        const humanReadable = date.toLocaleString('en-IN', options);
        return humanReadable;
      },
      
      async renderBMIChart(hdata) {
        const canvas = document.getElementById('bmiChart');
      if (!canvas) {
        console.error('Canvas element not found!');
        return;
      }
        if (!hdata) {
            console.error('No health data available.');
            return;
        }

        const labels = await hdata.map(record => this.dat(record.recorded_at)); // Date as x-axis
        const bmiData = await hdata.map(record => record.health_data.bmi); // BMI data

        // const labels = [1,2,3,4,5]
        // const bmiData = [1,2,3,4,5]

        const ctx = document.getElementById('bmiChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'BMI',
                    data: bmiData,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    // backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    // fill: true,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        title: {display: true, text: 'Date'}
                    },
                    y: {
                        title: {display: true, text: 'BMI'},
                        min: 15
                    }
                }
            }
        });
        }
    }
};


