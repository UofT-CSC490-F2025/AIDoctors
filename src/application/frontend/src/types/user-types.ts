export type User = {
  firstName: string;
  lastName: string;
  username: string;
  email: string;
  disabled: boolean;
  roles: string[];
};

export type UserContext = {
  user: User | null;
  setUser: (u: User | null) => void;
  isLoading: boolean;
};
