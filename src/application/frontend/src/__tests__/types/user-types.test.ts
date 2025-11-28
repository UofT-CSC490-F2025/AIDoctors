/// <reference types="@testing-library/jest-dom" />
import { describe, expect, it } from '@jest/globals';
import { User } from '@/types/user-types';

describe('User Types', () => {
  describe('User Type', () => {
    it('should accept valid User with all required fields', () => {
      const validUser: User = {
        firstName: 'John',
        lastName: 'Doe',
        username: 'johndoe',
        email: 'john.doe@example.com',
        disabled: false,
        roles: ['user'],
      };

      expect(validUser).toBeDefined();
      expect(validUser.firstName).toBe('John');
      expect(validUser.lastName).toBe('Doe');
      expect(validUser.username).toBe('johndoe');
      expect(validUser.email).toBe('john.doe@example.com');
      expect(validUser.disabled).toBe(false);
      expect(validUser.roles).toEqual(['user']);
    });

    it('should accept User with multiple roles', () => {
      const adminUser: User = {
        firstName: 'Admin',
        lastName: 'User',
        username: 'admin',
        email: 'admin@example.com',
        disabled: false,
        roles: ['user', 'admin', 'moderator'],
      };

      expect(adminUser.roles).toHaveLength(3);
      expect(adminUser.roles).toContain('user');
      expect(adminUser.roles).toContain('admin');
      expect(adminUser.roles).toContain('moderator');
    });

    it('should accept User with empty roles array', () => {
      const userNoRoles: User = {
        firstName: 'Guest',
        lastName: 'User',
        username: 'guest',
        email: 'guest@example.com',
        disabled: false,
        roles: [],
      };

      expect(userNoRoles.roles).toHaveLength(0);
      expect(userNoRoles.roles).toEqual([]);
    });

    it('should accept User with disabled true', () => {
      const disabledUser: User = {
        firstName: 'Disabled',
        lastName: 'Account',
        username: 'disabled',
        email: 'disabled@example.com',
        disabled: true,
        roles: ['user'],
      };

      expect(disabledUser.disabled).toBe(true);
    });

    it('should accept User with disabled false', () => {
      const activeUser: User = {
        firstName: 'Active',
        lastName: 'Account',
        username: 'active',
        email: 'active@example.com',
        disabled: false,
        roles: ['user'],
      };

      expect(activeUser.disabled).toBe(false);
    });

    it('should accept User with various email formats', () => {
      const emailFormats = [
        'simple@example.com',
        'user.name@example.com',
        'user+tag@example.co.uk',
        'user_name123@sub.domain.example.org',
      ];

      emailFormats.forEach((email) => {
        const user: User = {
          firstName: 'Test',
          lastName: 'User',
          username: 'testuser',
          email: email,
          disabled: false,
          roles: ['user'],
        };

        expect(user.email).toBe(email);
      });
    });

    it('should accept User with various username formats', () => {
      const usernames = [
        'simple',
        'user123',
        'user_name',
        'user-name',
        'User123',
        'u',
      ];

      usernames.forEach((username) => {
        const user: User = {
          firstName: 'Test',
          lastName: 'User',
          username: username,
          email: 'test@example.com',
          disabled: false,
          roles: ['user'],
        };

        expect(user.username).toBe(username);
      });
    });

    it('should accept User with first and last names containing spaces and special characters', () => {
      const user: User = {
        firstName: "Mary-Jane O'Connor",
        lastName: "De La Cruz-Smith",
        username: 'mjanes',
        email: 'mary@example.com',
        disabled: false,
        roles: ['user'],
      };

      expect(user.firstName).toBe("Mary-Jane O'Connor");
      expect(user.lastName).toBe("De La Cruz-Smith");
    });

    it('should handle typical user object', () => {
      const typicalUser: User = {
        firstName: 'Jane',
        lastName: 'Smith',
        username: 'janesmith',
        email: 'jane.smith@company.com',
        disabled: false,
        roles: ['user', 'editor'],
      };

      expect(typicalUser.firstName).toBe('Jane');
      expect(typicalUser.roles).toContain('editor');
      expect(typicalUser.disabled).toBe(false);
    });

    it('should accept User with single character names', () => {
      const user: User = {
        firstName: 'A',
        lastName: 'B',
        username: 'ab',
        email: 'a@b.com',
        disabled: false,
        roles: ['user'],
      };

      expect(user.firstName).toBe('A');
      expect(user.lastName).toBe('B');
    });

    it('should accept User with long names', () => {
      const longFirstName = 'Christopher Alexander';
      const longLastName = 'Montgomery-Williamson III';

      const user: User = {
        firstName: longFirstName,
        lastName: longLastName,
        username: 'camw3',
        email: 'chris.montgomery@example.com',
        disabled: false,
        roles: ['user'],
      };

      expect(user.firstName).toBe(longFirstName);
      expect(user.lastName).toBe(longLastName);
    });

    it('should preserve all User properties', () => {
      const originalUser: User = {
        firstName: 'Original',
        lastName: 'User',
        username: 'original',
        email: 'original@example.com',
        disabled: true,
        roles: ['admin', 'user'],
      };

      const copiedUser: User = { ...originalUser };

      expect(copiedUser).toEqual(originalUser);
      expect(copiedUser.firstName).toBe(originalUser.firstName);
      expect(copiedUser.lastName).toBe(originalUser.lastName);
      expect(copiedUser.username).toBe(originalUser.username);
      expect(copiedUser.email).toBe(originalUser.email);
      expect(copiedUser.disabled).toBe(originalUser.disabled);
      expect(copiedUser.roles).toEqual(originalUser.roles);
    });

    it('should accept User with numeric strings in names', () => {
      const user: User = {
        firstName: 'John123',
        lastName: 'Doe456',
        username: 'john123',
        email: 'john123@example.com',
        disabled: false,
        roles: ['user'],
      };

      expect(user.firstName).toBe('John123');
      expect(user.lastName).toBe('Doe456');
    });

    it('should accept User with role hierarchy', () => {
      const superAdminUser: User = {
        firstName: 'Super',
        lastName: 'Admin',
        username: 'superadmin',
        email: 'superadmin@example.com',
        disabled: false,
        roles: ['user', 'moderator', 'admin', 'superadmin'],
      };

      expect(superAdminUser.roles).toHaveLength(4);
      expect(superAdminUser.roles[0]).toBe('user');
      expect(superAdminUser.roles[3]).toBe('superadmin');
    });

    it('should accept User representing a system account', () => {
      const systemUser: User = {
        firstName: 'System',
        lastName: 'Account',
        username: 'system',
        email: 'system@internal.com',
        disabled: false,
        roles: ['system', 'automated'],
      };

      expect(systemUser.username).toBe('system');
      expect(systemUser.roles).toContain('system');
      expect(systemUser.roles).toContain('automated');
    });
  });
});
