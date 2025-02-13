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
                                <div class="container" >
                                    <button class="btn btn-2"
                                        v-for="(value, key) in showData" :key="key" 
                                        :class="{ active: selectedAttribute === key }" 
                                        @click="btnClick(key)">
                                        {{ formatKey(key) }}
                                        </button>
                                </div>
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
                                        <td v-for="(value, key) in record.health_data" :key="key">{{ value }}</td>
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
        showData: {},
        selectedAttribute: '',
        chartInstance: null,
    };
  },


  async mounted() {
    try {
        const id = 3;
        const response = await fetch(`/health-tracker/${id}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Failed to fetch data.');
        }
        this.healthData = data;
        const hdata = this.healthData.data;
        this.initializeShowData(hdata);
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
          year: '2-digit', // Example: "2025"
          month: 'short', // Example: "Jan"
          day: 'numeric', // Example: "16"
          hour: '2-digit', // Example: "04"
          minute: '2-digit', // Example: "18"
        //   second: '2-digit', // Example: "02"
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

      initializeShowData(hdata) {
        // Dynamically create showData object based on the keys in health_data
        if (hdata && hdata.length > 0 && hdata[0].health_data) {
          const keys = Object.keys(hdata[0].health_data);
          keys.forEach(key => {
            this.$set(this.showData, key, false); 
          });
            this.showData[keys[0]] = true;
            this.selectedAttribute = keys[0];
        }
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

        if (this.selectedAttribute) {
            datasets.push({
              label: this.formatKey(this.selectedAttribute),
              data: hdata.map((record) => record.health_data[this.selectedAttribute]),
              borderColor: '#2A9D8F',
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
    
    btnClick(key) {
        // Toggle the selected attribute
        this.selectedAttribute = key;
        this.selectAttribute();
      },

      selectAttribute() {
        // When the selected attribute changes, re-render the chart
        const hdata = this.healthData.data;
        this.renderChart(hdata);
      },

      getBorderColor(key) {
        // Assign colors dynamically based on the field key (you can customize this)

        const colors = {
          bmi: 'rgba(75, 192, 192, 1)',
          body_fat_percentage: 'rgba(255, 99, 132, 1)',
          calories_burned: 'rgba(54, 162, 235, 1)',
          steps: 'rgba(153, 102, 255, 1)',
          weight: 'rgba(255, 159, 64, 1)',
        };
        return colors[key] || 'rgba(0, 0, 0, 1)'; // Default color
      },

    }
};


