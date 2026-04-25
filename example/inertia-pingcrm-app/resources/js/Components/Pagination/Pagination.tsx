import { Link } from '@inertiajs/react';
import classNames from 'classnames';

interface PaginationMeta {
  current_page: number;
  last_page: number;
}

interface PaginationProps {
  meta: PaginationMeta;
}

export default function Pagination({ meta }: PaginationProps) {
  const { current_page, last_page } = meta;

  if (last_page <= 1) return null;

  const links = [
    {
      label: '&laquo; Previous',
      url: current_page > 1 ? `?page=${current_page - 1}` : null,
      active: false,
    },
    ...Array.from({ length: last_page }, (_, i) => ({
      label: String(i + 1),
      url: `?page=${i + 1}`,
      active: i + 1 === current_page,
    })),
    {
      label: 'Next &raquo;',
      url: current_page < last_page ? `?page=${current_page + 1}` : null,
      active: false,
    },
  ];

  return (
    <div className="flex flex-wrap mt-6 -mb-1">
      {links.map(link =>
        link.url === null ? (
          <PageInactive key={link.label} label={link.label} />
        ) : (
          <PageItem key={link.label} {...link} />
        )
      )}
    </div>
  );
}

interface PageItemProps {
  url: string;
  label: string;
  active: boolean;
}

function PageItem({ active, label, url }: PageItemProps) {
  const className = classNames(
    ['mr-1 mb-1', 'px-4 py-3', 'border border-solid border-gray-300 rounded', 'text-sm', 'hover:bg-white', 'focus:outline-none focus:border-indigo-700 focus:text-indigo-700'],
    { 'bg-white': active }
  );

  return (
    <Link className={className} href={url}>
      <span dangerouslySetInnerHTML={{ __html: label }} />
    </Link>
  );
}

function PageInactive({ label }: { label: string }) {
  return (
    <div
      className="mr-1 mb-1 px-4 py-3 text-sm border rounded border-solid border-gray-300 text-gray"
      dangerouslySetInnerHTML={{ __html: label }}
    />
  );
}
