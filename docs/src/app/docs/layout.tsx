import { source } from '@/lib/source';
import { DocsLayout, DocsLayoutProps } from 'fumadocs-ui/layouts/docs';
import { baseOptions } from '@/lib/layout.shared';
import { GithubInfo } from 'fumadocs-ui/components/github-info';
import { ThemeToggle } from '@/components/theme-toggle';
import { Github } from 'lucide-react';

function docsOptions(): DocsLayoutProps {
  return {
    ...baseOptions(),
    tree: source.pageTree,
    links: [
      {
        type: 'custom',
        children: (
          <GithubInfo owner="fuma-nama" repo="fumadocs" className="lg:-mx-2 px-4" />
        ),
      },
    ],
  };
}

// export default function Layout({ children }: { children: React.ReactNode }) {
//   return <DocsLayout {...docsOptions()}>{children}</DocsLayout>;
// }
export default function Layout({ children }: LayoutProps<'/docs'>) {
  return (
    <DocsLayout tree={source.pageTree} {...baseOptions()}>
      {children}
    </DocsLayout>
  );
}
