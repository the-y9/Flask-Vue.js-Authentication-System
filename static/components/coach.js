export default {
    template:`  <div>
                    <section class="poster">
                        <div class="poster-content">
                            <h1 class="poster-tile">Hi, {{ username }}</h1>
                            <p class="poster-subtitle">Sort and manage your club.</p>
                        </div>
                    </section>

                    <section class="features">
                        <div class="container">
                            <div class="row">
                                <div class="col-md-9">
                                    <canvas id="bmiChart" width="100%"></canvas>
                                </div>
                                <div class="col-md-3">
                                    <br><br><br>
                                    <button class='btn btn-info ' @click="toggleChartData">Toggle Data</button>
                                </div>
                            </div>    
                        </div>
                            
                        <!-- Check if health data is available -->
                        <div v-if="healthData && healthData.data">
            
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Recorded At</th>
                                        <th v-for="(value, key) in healthData.data[0].health_data" :key="key">{{ formatKey(key) }}</th>
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
        order: 0,
        chartInstance: null,
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
        this.renderChart(hdata);
    } catch (error) {
        console.error('Error fetching data:', error);
    }    
        
    },

  methods: {
    formatKey(key) {
        // Format the key for table headers (e.g., bmi -> BMI)
        return key.replace(/_/g, ' ').toUpperCase();
      },  
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
      
      async renderChart(hdata) {
        const canvas = document.getElementById('bmiChart');
        if (!canvas) {
            console.error('Canvas element not found!');
            return;
        }
        if (!hdata) {
            console.error('No health data available.');
            return;
        }

        const labels = hdata.map((record) => this.dat(record.recorded_at)); // Date as x-axis

        const datasets = [];

        // Add each dataset conditionally based on the toggled values
        if (this.showBMI) {
            datasets.push({
                label: 'BMI',
                data: hdata.map((record) => record.health_data.bmi),
                borderColor: 'rgba(75, 192, 192, 1)',
                tension: 0.1,
            });
        }

        if (this.showBodyFat) {
            datasets.push({
                label: 'Body Fat Percentage',
                data: hdata.map((record) => record.health_data.body_fat_percentage),
                borderColor: 'rgba(255, 99, 132, 1)',
                tension: 0.1,
            });
        }

        if (this.showCalories) {
            datasets.push({
                label: 'Calories Burned',
                data: hdata.map((record) => record.health_data.calories_burned),
                borderColor: 'rgba(54, 162, 235, 1)',
                tension: 0.1,
            });
        }

        if (this.showSteps) {
            datasets.push({
                label: 'Steps',
                data: hdata.map((record) => record.health_data.steps),
                borderColor: 'rgba(153, 102, 255, 1)',
                tension: 0.1,
            });
        }

        if (this.showWeight) {
            datasets.push({
                label: 'Weight',
                data: hdata.map((record) => record.health_data.weight),
                borderColor: 'rgba(255, 159, 64, 1)',
                tension: 0.1,
            });
        }

        const ctx = canvas.getContext('2d');

        if (this.chartInstance) {
            this.chartInstance.destroy();
          }

        this.chartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: datasets,
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        title: { display: true, text: 'Date' },
                    },
                    y: {
                        title: { display: true, text: 'Values' },
                        min: 0,
                    },
                },
            },
        });
    },

    toggleChartData() {
        this.order = (this.order + 1)%5;

        if (this.order === 0){
            this.showWeight = false;
            this.showBMI = true;
        }else if (this.order === 1){
            this.showBMI = false;
            this.showBodyFat = true;
        }else if (this.order === 2){
            this.showBodyFat = false;
            this.showCalories = true;
        }else if (this.order === 3){
            this.showCalories = false;
            this.showSteps = true;
        }else if (this.order === 4){
            this.showSteps = false;
            this.showWeight = true;
        }

        const hdata = this.healthData.data;
        this.renderChart(hdata);
    },
    }
};


