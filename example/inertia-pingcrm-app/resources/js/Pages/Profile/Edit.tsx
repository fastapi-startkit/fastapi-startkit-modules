import React from 'react';
import { Head, usePage, useForm } from '@inertiajs/react';
import MainLayout from '@/Layouts/MainLayout';
import LoadingButton from '@/Components/Button/LoadingButton';
import TextInput from '@/Components/Form/TextInput';
import FileInput from '@/Components/Form/FileInput';
import FieldGroup from '@/Components/Form/FieldGroup';

interface ProfileUser {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  photo: string | null;
  password: string;
}

const Edit = () => {
  const { user } = usePage<{ user: ProfileUser }>().props;

  const { data, setData, errors, post, processing } = useForm({
    first_name: user.first_name || '',
    last_name: user.last_name || '',
    email: user.email || '',
    password: '',
    photo: null as File | null,
    _method: 'post',
  });

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    post('/profile', { forceFormData: true });
  }

  return (
    <div>
      <Head title="My Profile" />
      <h1 className="mb-8 text-3xl font-bold">My Profile</h1>
      <div className="max-w-3xl overflow-hidden bg-white rounded shadow">
        <form onSubmit={handleSubmit}>
          <div className="grid gap-8 p-8 lg:grid-cols-2">
            <FieldGroup label="First Name" name="first_name" error={errors.first_name}>
              <TextInput
                name="first_name"
                error={errors.first_name}
                value={data.first_name}
                onChange={e => setData('first_name', e.target.value)}
              />
            </FieldGroup>

            <FieldGroup label="Last Name" name="last_name" error={errors.last_name}>
              <TextInput
                name="last_name"
                error={errors.last_name}
                value={data.last_name}
                onChange={e => setData('last_name', e.target.value)}
              />
            </FieldGroup>

            <FieldGroup label="Email" name="email" error={errors.email}>
              <TextInput
                name="email"
                type="email"
                error={errors.email}
                value={data.email}
                onChange={e => setData('email', e.target.value)}
              />
            </FieldGroup>

            <FieldGroup label="Password" name="password" error={errors.password}>
              <TextInput
                name="password"
                type="password"
                error={errors.password}
                value={data.password}
                onChange={e => setData('password', e.target.value)}
              />
            </FieldGroup>

            <FieldGroup label="Photo" name="photo" error={errors.photo}>
              <FileInput
                name="photo"
                accept="image/*"
                error={errors.photo}
                existingPhotoUrl={user.photo as string}
                onChange={file => setData('photo', file)}
              />
            </FieldGroup>
          </div>
          <div className="flex items-center justify-end px-8 py-4 bg-gray-100 border-t border-gray-200">
            <LoadingButton loading={processing} type="submit" className="btn-indigo">
              Save Changes
            </LoadingButton>
          </div>
        </form>
      </div>
    </div>
  );
};

Edit.layout = (page: React.ReactNode) => <MainLayout children={page} />;

export default Edit;
