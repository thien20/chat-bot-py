import http from 'k6/http';
import { sleep } from 'k6';
import { check } from 'k6';

// Define stages with variable CCU and durations
export let options = {
    stages: [
        { duration: '1m', target: 100 }, // Ramp-up to 10 VUs
        { duration: '5m', target: 1000 }, // Maintain 20 VUs
        { duration: '30s', target: 50 },  // Ramp-down to 0 VUs
    ],
    thresholds: {
        http_req_duration: ['p(95)<200'], // 95% of requests should be <500ms
    },
};

// export function handleSummary(res) {
    
//     const parse_json = JSON.parse(res.body);

//     return {
//         'message' : parse_json.response,
//     };
// }

export default function () {
    const url = 'http://127.0.0.1:8000/chat/vn'; // Adjust as needed
    const payload = JSON.stringify({ message: "viết hàm fibonacci bằng python" });

    const params = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    let res = http.post(url, payload, params);
    // console.log(JSON.parse(res.body).response);
    
    // Verify response
    check(res, {
        'status is 200': (r) => r.status === 200,
        'response time < 500ms': (r) => r.timings.duration < 500,
    });

    // handleSummary(res)
    sleep(1); // Wait between requests
}
