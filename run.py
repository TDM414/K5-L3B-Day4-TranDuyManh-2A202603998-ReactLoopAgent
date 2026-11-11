import argparse
import json
import os
import sys

# Tự động nạp file .env nếu có mà không phụ thuộc thư viện bên thứ ba
def _load_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if line.startswith('export '):
                    line = line[7:].strip()
                if '=' in line:
                    k, v = line.split('=', 1)
                    k, v = k.strip(), v.strip().strip('"\'')
                    if k and k not in os.environ:
                        os.environ[k] = v

_load_env()

from agent import run_agent
from providers import Provider
from status_tools import StatusTools
from bonus.tools import BonusTools


def run(question, mode, provider_name, model, max_steps, fail=False, bonus=False):
    provider = Provider(provider_name, model)
    tools = BonusTools(mode) if bonus else StatusTools(mode, fail=fail)
    return run_agent(question, provider, tools, max_steps=max_steps)


def main():
    p = argparse.ArgumentParser(description='Chạy status agent')
    p.add_argument('question', help='Câu hỏi cho agent')
    p.add_argument('--bonus', action='store_true', help='Dùng bộ tools bonus')
    p.add_argument('--mode', choices=['snapshot', 'live'], default='snapshot')
    p.add_argument('--provider', choices=['openai', 'gemini', 'anthropic', 'openrouter'], default=os.getenv('PROVIDER', 'openai'))
    p.add_argument('--model', default=os.getenv('MODEL'))
    p.add_argument('--max-steps', type=int, default=6)
    args = p.parse_args()
    if args.max_steps < 1:
        p.error('--max-steps phải >= 1')
    try:
        result = run(args.question, args.mode, args.provider, args.model, args.max_steps, bonus=args.bonus)
    except (ValueError, RuntimeError, NotImplementedError) as exc:
        print(f'Lỗi: {exc}', file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['status'] == 'completed' else 1

if __name__ == '__main__':
    sys.exit(main())
