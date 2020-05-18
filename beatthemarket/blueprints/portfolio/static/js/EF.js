$(document).ready(
    async function () {

        $('.viz').hide();
        // page loader
        $('.page-overlay').css('height', window.innerHeight);

        let counter = 0;

        function progressSim() {

            document.querySelector('.page-overlay>.text>p').innerHTML = 'Analyzing Portfolio ... ' + counter + '%';
            if (counter >= 100) {
                clearTimeout(sim);
            }
            counter++;
        }

        var sim = setInterval(progressSim, 200);

        let response = await loadEFData()

        try {
            if (response.status === 200) {
                $('.page-overlay').hide();
                $('.viz').show()
            }
        } catch (e) {
            $('.page-overlay').hide();
            $('.viz').hide()
            alert("Insight is available when holding records are available.")
            location.href = '/portfolio/holding'
        }
    })


async function loadEFData() {
    try {
        let res = await axios.get('/portfolio/visualization/data')

        let tbl = JSON.parse(res.data['tbl'])
        Plotly.newPlot('tbl', tbl)

        let alloc = JSON.parse(res.data['alloc'])
        Plotly.newPlot('alloc', alloc)

        let ef = JSON.parse(res.data['ef'])
        Plotly.newPlot('ef', ef)

        let sim = JSON.parse(res.data['sim'])
        Plotly.newPlot('sim', sim)

        return res
    } catch (e) {
        console.log(e)
    }
}
