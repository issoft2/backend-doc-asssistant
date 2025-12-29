import axios from 'axios';

export function listUsers() {
    return axios.get('/admin/users');
}

export function getUser(userId: string) {
    return axios.get(`/admin/users/${userId}`);
}

export function updateUser(userId: string, payload: any) {
    return axios.patch(`/admin/users/${userId}`, payload);
}

export function deactivateUser(userId: string) {
    return axios.post(`/admin/users/${userId}/deactivate`);
}