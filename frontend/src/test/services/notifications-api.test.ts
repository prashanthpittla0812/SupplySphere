import { describe, it, expect, vi, beforeEach } from 'vitest';
import api from '../../app/services/api';
import { notificationsApi } from '../../app/services/notifications-api';

vi.mock('../../app/services/api', () => ({
  default: {
    get: vi.fn(),
    patch: vi.fn(),
  },
}));

const mockedApi = vi.mocked(api);

describe('notificationsApi', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('getAll calls GET /notifications with params', () => {
    const params = { page: 1 };
    notificationsApi.getAll(params);
    expect(mockedApi.get).toHaveBeenCalledWith('/notifications', { params });
  });

  it('markRead calls PATCH /notifications/:id/read', () => {
    notificationsApi.markRead('n1');
    expect(mockedApi.patch).toHaveBeenCalledWith('/notifications/n1/read');
  });

  it('markAllRead calls PATCH /notifications/read-all', () => {
    notificationsApi.markAllRead();
    expect(mockedApi.patch).toHaveBeenCalledWith('/notifications/read-all');
  });

  it('getUnreadCount calls GET /notifications/unread-count', () => {
    notificationsApi.getUnreadCount();
    expect(mockedApi.get).toHaveBeenCalledWith('/notifications/unread-count');
  });
});
